import typing as t

from .abstract import RemoteService
from .serializers import GitlabRepositorySync, GitlabOrganizationSync
from .enums import GitlabNamespaceKind


class GitlabService(RemoteService):
    repository_sync_serializer = GitlabRepositorySync
    organization_sync_serializer = GitlabOrganizationSync

    def get_user_repos(self) -> t.List[dict]:
        return self.client.get("projects/?membership=True&archived=False", token=self.token).json()

    def get_repository_languages(self, repository_id: str) -> dict:
        return self.client.get(f"projects/{repository_id}/languages", token=self.token).json()

    def get_user_organizations(self) -> t.List[dict]:
        return self.client.get("groups/?all_available=False&archived=False", token=self.token).json()

    def parse_organization_id_and_name(self, repository_data: dict) -> t.Optional[t.Tuple[int, str]]:
        if repository_data["namespace"]["kind"] == GitlabNamespaceKind.ORGANIZATION:
            return repository_data["namespace"]["id"], repository_data["namespace"]["name"]
        return None
