import typing as t

import hashlib
import hmac

from rest_framework.request import Request
from rest_framework.response import Response

from .abstract import RemoteService
from .serializers import GitHubRepositorySync, GithubOrganizationSync, GitHubIssueSync, GitHubUserSerializer
from .enums import GitHubOwnerType
from .constants import Messages, Headers, Events, IssueEventActions
from openwiden.repositories import models as repo_models, services as repo_services
from openwiden.organizations import models as org_models
from django.utils.translation import gettext_lazy as _
from openwiden import exceptions
from openwiden.services import models as service_models
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
    repo_sync_serializer = GitHubRepositorySync
    org_sync_serializer = GithubOrganizationSync
    issue_sync_serializer = GitHubIssueSync
    user_profile_serializer = GitHubUserSerializer

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

    def create_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        data = dict(
            events=["issues", "repository"],
            config=dict(
                url=webhook.url,
                content_type="json",
                secret=webhook.secret,
                insecure_ssl="0",
            )
        )
        owner = self.get_repo_owner(webhook.repository)
        response = self.client.post(f"/repos/{owner}/{webhook.repository.name}/hooks", token=self.token, json=data)
        json = response.json()

        if response.status_code == 201:
            webhook.remote_id = json["id"]
            webhook.is_active = True
            webhook.created_at = json["created_at"]
            webhook.updated_at = json["updated_at"]
            webhook.issue_events_enabled = True
            webhook.save(update_fields=("remote_id", "is_active", "created_at", "updated_at", "issue_events_enabled"))
        else:
            raise exceptions.ServiceException(Messages.REPO_WEBHOOK_CREATE_ERROR.format(error=json))

    def update_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        pass

    def repo_webhook_exist(self, repo: repo_models.Repository, webhook_id: int) -> bool:
        pass

    @classmethod
    def handle_webhook(cls, webhook: webhook_models.RepositoryWebhook, request: Request) -> Response:
        # Check headers exist or not
        if request.META.get(Headers.SIGNATURE) is None:
            raise exceptions.ServiceException(Messages.X_HUB_SIGNATURE_HEADER_IS_MISSING)
        elif request.META.get(Headers.EVENT) is None:
            raise exceptions.ServiceException(Messages.X_GITHUB_EVENT_HEADER_IS_MISSING)

        # Check digest required name and get signature
        digest_name, signature = request.META[Headers.SIGNATURE].split("=")
        if digest_name != "sha1":
            raise exceptions.ServiceException(Messages.DIGEST_IS_NOT_SUPPORTED.format(digest_name=digest_name))

        # Compare received signature
        if not cls._compare_signatures(webhook, request.body, signature):
            raise exceptions.ServiceException(Messages.X_HUB_SIGNATURE_IS_INVALID)

        event = request.META[Headers.EVENT]

        if event == Events.ISSUES:
            cls.handle_issue_event(webhook, request.data)
            return Response("Ok")
        if event == Events.PING:
            return Response("Pong")
        else:
            raise exceptions.ServiceException(f"unsupported event {event}")

    @classmethod
    def parse_issue_data(cls, data: dict) -> dict:
        return dict(
            remote_id=data["id"],
            title=data["title"],
            description=data["body"],
            state=data["state"],
            labels=[label["name"] for label in data["labels"]],
            url=data["html_url"],
            created_at=data["created_at"],
            closed_at=data["closed_at"],
            updated_at=data["updated_at"],
        )

    @classmethod
    def handle_issue_event(cls, webhook: webhook_models.RepositoryWebhook, data):
        action = data["action"]
        issue_data = cls.parse_issue_data(data["issue"])

        if action == IssueEventActions.DELETED:
            repo_services.Issue.delete_by_remote_id(webhook.repository, issue_data["remote_id"])
        else:
            repo_services.Issue.sync(webhook.repository, **issue_data)
