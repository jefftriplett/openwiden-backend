import typing as t

from .abstract import RemoteService
from .serializers import GitHubRepositorySync, GithubOrganizationSync
from .enums import GitHubOwnerType
from openwiden.repositories import models as repositories_models


class GitHubService(RemoteService):
    repository_sync_serializer = GitHubRepositorySync
    organization_sync_serializer = GithubOrganizationSync

    def get_user_repos(self) -> t.List[dict]:
        return self.client.get("user/repos", token=self.token).json()

    def get_repository_languages(self, repository: repositories_models.Repository) -> list:
        owner = self.oauth_token.login if repository.owner else repository.organization.name
        return list(self.client.get(f"repos/{owner}/{repository.name}/languages", token=self.token).json().keys())

    def get_user_organizations(self) -> t.List[dict]:
        data = self.client.get("user/orgs", token=self.token).json()

        # GitHub repository list contains only simple data, that's why it's required to call
        # additional request for each organization to get full data.
        full_data = []
        for organization in data:
            d = self.client.get(organization["url"], token=self.token).json()
            full_data.append(d)

        return full_data

    def parse_organization_id_and_name(self, repository_data: dict) -> t.Optional[t.Tuple[int, str]]:
        if repository_data["owner"]["type"] == GitHubOwnerType.ORGANIZATION:
            return repository_data["owner"]["id"], repository_data["owner"]["login"]
        return None
