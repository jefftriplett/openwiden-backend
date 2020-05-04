import typing as t

from . import exceptions
from .abstract import RemoteService
from .serializers import GitHubRepositorySync, GithubOrganizationSync
from .enums import GitHubOwnerType
from openwiden.repositories import models as repositories_models
from openwiden.organizations import models as org_models
from django.utils.translation import gettext_lazy as _


class GitHubService(RemoteService):
    repository_sync_serializer = GitHubRepositorySync
    organization_sync_serializer = GithubOrganizationSync

    @staticmethod
    def convert_repository_languages_lines_count_to_percentage(repository_languages: dict) -> dict:
        total_lines_count = sum(repository_languages.values())
        for k, v in repository_languages.items():
            repository_languages[k] = round(v / total_lines_count * 100, 2)
        return repository_languages

    def get_user_repos(self) -> t.List[dict]:
        repositories = self.client.get(
            "user/repos?affiliation=owner,organization_member&visibility=public", token=self.token
        ).json()
        return [repo for repo in repositories if repo["archived"] is False]

    def get_repository_languages(self, repository: repositories_models.Repository) -> dict:
        owner = self.oauth_token.login if repository.owner else repository.organization.name
        languages = self.client.get(f"repos/{owner}/{repository.name}/languages", token=self.token).json()
        languages = self.convert_repository_languages_lines_count_to_percentage(languages)
        return languages

    def parse_organization_slug(self, repository_data: dict) -> t.Optional[str]:
        if repository_data["owner"]["type"] == GitHubOwnerType.ORGANIZATION:
            return repository_data["owner"]["login"]
        return None

    def get_organization(self, org: str) -> dict:
        return self.client.get(f"orgs/{org}", token=self.token).json()

    def check_org_membership(self, organization: org_models.Organization) -> t.Tuple[bool, bool]:
        r = self.client.get(f"/user/memberships/orgs/{organization.name}", token=self.token)

        if r.status_code == 200:
            return True, r.json()["role"] == "admin"
        elif r.status_code == 404:
            return False, False
        else:
            raise exceptions.RemoteSyncException(
                _("an error occurred while check organization membership, please, try again.")
            )
