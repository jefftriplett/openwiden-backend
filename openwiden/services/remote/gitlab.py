import typing as t

from . import exceptions
from .abstract import RemoteService
from .serializers import GitlabRepositorySync, GitlabOrganizationSync, GitlabIssueSync
from .enums import GitlabNamespaceKind
from openwiden.organizations import models as org_models
from openwiden.repositories import models as repo_models
from django.utils.translation import gettext_lazy as _


class GitlabService(RemoteService):
    repo_sync_serializer = GitlabRepositorySync
    org_sync_serializer = GitlabOrganizationSync
    issue_sync_serializer = GitlabIssueSync

    def get_user_repos(self) -> t.List[dict]:
        return self.client.get("projects/?membership=True&archived=False&visibility=public", token=self.token).json()

    def get_repo_languages(self, repo: repo_models.Repository) -> dict:
        r = self.client.get(f"projects/{repo.remote_id}/languages", token=self.token)

        if r.status_code == 200:
            return r.json()
        else:
            raise exceptions.RemoteSyncException(_("Unexpected error occurred. API response: {r}").format(r=r.json()))

    def get_repo_issues(self, repo: repo_models.Repository) -> t.List[dict]:
        r = self.client.get(f"projects/{repo.remote_id}/issues?state=opened", token=self.token)

        if r.status_code == 200:
            return r.json()
        else:
            raise exceptions.RemoteSyncException(_("Unexpected error occurred. API response: {r}").format(r=r.json()))

    def parse_org_slug(self, repo_data: dict) -> t.Optional[str]:
        if repo_data["namespace"]["kind"] == GitlabNamespaceKind.ORGANIZATION:
            return repo_data["namespace"]["name"]
        return None

    def get_org(self, organization_id: str) -> dict:
        r = self.client.get(f"groups/{organization_id}", token=self.token)

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            raise exceptions.RemoteSyncException(
                _("Organization with id {org} is private or not found").format(org=organization_id)
            )
        else:
            raise exceptions.RemoteSyncException(_("Unexpected error occurred. API response: {r}").format(r=r.json()))

    def check_org_membership(self, organization: org_models.Organization) -> t.Tuple[bool, bool]:
        r = self.client.get(f"groups/{organization.remote_id}/members/{self.oauth_token.remote_id}", token=self.token)

        if r.status_code == 200:
            return True, r.json()["access_level"] >= 40
        elif r.status_code == 404:
            return False, False
        else:
            raise exceptions.RemoteSyncException(r.json())
