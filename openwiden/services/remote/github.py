import typing as t

from .abstract import RemoteService
from .serializers import GitHubRepositorySync, GithubOrganizationSync
from .enums import GitHubOwnerType

from openwiden.organizations import models as organizations_models


class GitHubService(RemoteService):
    repository_sync_serializer = GitHubRepositorySync
    organization_sync_serializer = GithubOrganizationSync

    def get_user_repos(self) -> t.List[dict]:
        # TODO: pagination
        return self.client.get("user/repos", token=self.token).json()

    def get_repository_languages(self, full_name: str) -> dict:
        return self.client.get(f"repos/{full_name}/languages", token=self.token).json()

    def get_user_organizations(self) -> t.List[dict]:
        organizations = self.client.get("user/orgs", token=self.token).json()
        full_data = []
        for org in organizations:
            data = self.client.get(org["url"], token=self.token).json()
            full_data.append(data)
        return full_data

    def get_repository_organization(self, data: dict) -> t.Optional[organizations_models.Organization]:
        if data["owner"]["type"] == GitHubOwnerType.ORGANIZATION:
            organization, updated = organizations_models.Organization.objects.get_or_create(
                version_control_service=self.provider,
                remote_id=data["owner"]["id"],
                defaults=dict(name=data["owner"]["login"]),
            )
            return organization
        return None
