import typing as t

from .abstract import RemoteService
from .serializers import GitlabRepositorySync
from .enums import GitlabNamespaceKind

from openwiden.organizations import models as organizations_models


class GitlabService(RemoteService):
    repository_sync_serializer = GitlabRepositorySync

    def get_user_repos(self) -> t.List[dict]:
        # TODO: pagination
        data = self.client.get("projects/?membership=True", token=self.token).json()
        return data

    def get_repository_languages(self, repository_id: str) -> dict:
        return self.client.get(f"projects/{repository_id}/languages", token=self.token).json()

    def get_user_organizations(self) -> t.List[dict]:
        return []

    def get_repository_organization(self, data: dict) -> t.Optional[organizations_models.Organization]:
        if data["namespace"]["kind"] == GitlabNamespaceKind.ORGANIZATION:
            organization, created = organizations_models.Organization.objects.get_or_create(
                version_control_service=self.provider,
                remote_id=data["namespace"]["id"],
                defaults=dict(name=data["namespace"]["name"]),
            )
            return organization
        return None
