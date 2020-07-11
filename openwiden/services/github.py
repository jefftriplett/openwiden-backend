import typing as t

import hashlib
import hmac

from rest_framework.request import Request
from rest_framework.response import Response

from .abstract import RemoteService
from .serializers import GitHubRepositorySync, GithubOrganizationSync, GitHubIssueSync
from .enums import GitHubOwnerType
from .constants import Messages, Headers, Events, IssueEventActions
from openwiden.repositories import models as repo_models, services as repo_services
from openwiden.organizations import models as org_models
from django.utils.translation import gettext_lazy as _
from openwiden import exceptions
from openwiden.webhooks import models as webhook_models


def convert_lines_count_to_percent(repo_languages: dict) -> dict:
    """
    Converts repo languages lines count into percentages.
    """
    total_lines_count = sum(repo_languages.values())
    for k, v in repo_languages.items():
        repo_languages[k] = round(v / total_lines_count * 100, 2)
    return repo_languages


class GitHubService(RemoteService):
    def create_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        pass

    def update_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        pass

    def repo_webhook_exist(self, repo: repo_models.Repository, webhook_id: int) -> bool:
        pass

    @classmethod
    def handle_webhook(cls, webhook: webhook_models.RepositoryWebhook,
                       request: Request) -> Response:
        pass

    @classmethod
    def handle_issue_event(cls, webhook: webhook_models.RepositoryWebhook, data):
        pass

    repo_sync_serializer = GitHubRepositorySync
    org_sync_serializer = GithubOrganizationSync
    issue_sync_serializer = GitHubIssueSync

    def get_repo_owner(self, repo: repo_models.Repository) -> str:
        """
        Returns repo owner for required API calls.
        """
        return self.vcs_account.login if repo.owner else repo.organization.name

    def get_user_repos(self) -> t.List[dict]:
        repositories = self.client.get(
            "user/repos?affiliation=owner,organization_member&visibility=public", token=self.token
        ).json()
        return [repo for repo in repositories if repo["archived"] is False]

    def get_repo_languages(self, repo: repo_models.Repository) -> dict:
        owner = self.get_repo_owner(repo)
        languages = self.client.get(f"repos/{owner}/{repo.name}/languages", token=self.token).json()
        languages = convert_lines_count_to_percent(languages)
        return languages

    def get_repo_issues(self, repo: repo_models.Repository) -> t.List[dict]:
        owner = self.get_repo_owner(repo)
        r = self.client.get(f"repos/{owner}/{repo.name}/issues?state=open", token=self.token)
        if r.status_code == 200:
            # Note: GitHub's REST API v3 considers every pull request an issue,
            # but not every issue is a pull request. For this reason, "Issues"
            # endpoints may return both issues and pull requests in the response.
            # We can identify pull requests by the pull_request key.
            return [issue for issue in r.json() if "pull_request" not in issue]
        else:
            raise exceptions.ServiceException(
                _("an error occurred for repo issues sync, please, try again. API response: {r}").format(r=r.json())
            )

    def parse_org_slug(self, repo_data: dict) -> t.Optional[str]:
        if repo_data["owner"]["type"] == GitHubOwnerType.ORGANIZATION:
            return repo_data["owner"]["login"]
        return None

    def get_org(self, org: str) -> dict:
        return self.client.get(f"orgs/{org}", token=self.token).json()

    def check_org_membership(self, org: org_models.Organization) -> t.Tuple[bool, bool]:
        r = self.client.get(f"/user/memberships/orgs/{org.name}", token=self.token)

        if r.status_code == 200:
            return True, r.json()["role"] == "admin"
        elif r.status_code == 404:
            return False, False
        else:
            raise exceptions.ServiceException(
                _("an error occurred while check organization membership, please, try again.")
            )

    @staticmethod
    def _compare_signatures(webhook: webhook_models.RepositoryWebhook, msg, signature: str) -> bool:
        """
        Compares signature for received GitHub webhook.
        """
        generated = hmac.new(webhook.secret.encode("utf-8"), msg, hashlib.sha1)
        return True if hmac.compare_digest(generated.hexdigest(), signature) else False
