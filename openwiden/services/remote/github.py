import typing as t

from .abstract import RemoteService
from .serializers import GitHubRepositorySync, GithubOrganizationSync, GitHubIssueSync
from .enums import GitHubOwnerType
from openwiden.repositories import models as repo_models
from openwiden.organizations import models as org_models
from django.utils.translation import gettext_lazy as _
from openwiden import exceptions


class GitHubService(RemoteService):
    repo_sync_serializer = GitHubRepositorySync
    org_sync_serializer = GithubOrganizationSync
    issue_sync_serializer = GitHubIssueSync

    @staticmethod
    def convert_repo_lang_lines_count_to_percent(repo_languages: dict) -> dict:
        """
        Converts repo languages lines count into percentages.
        """
        total_lines_count = sum(repo_languages.values())
        for k, v in repo_languages.items():
            repo_languages[k] = round(v / total_lines_count * 100, 2)
        return repo_languages

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
        languages = self.convert_repo_lang_lines_count_to_percent(languages)
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
