import typing as t

from .abstract import RemoteService
from .serializers import GitHubRepositorySync, GithubOrganizationSync
from .enums import GitHubOwnerType


class GitHubService(RemoteService):
    repository_sync_serializer = GitHubRepositorySync
    organization_sync_serializer = GithubOrganizationSync

    def get_user_repos(self) -> t.List[dict]:
        return self.client.get("user/repos", token=self.token).json()

    def get_repository_languages(self, full_name: str) -> dict:
        return self.client.get(f"repos/{full_name}/languages", token=self.token).json()

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
