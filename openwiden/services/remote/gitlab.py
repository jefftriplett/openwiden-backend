import typing as t
from datetime import datetime

from . import exceptions, constants
from .abstract import RemoteService
from .serializers import GitlabRepositorySync, GitlabOrganizationSync, GitlabIssueSync
from .enums import GitlabNamespaceKind
from openwiden.organizations import models as org_models
from openwiden.repositories import models as repo_models
from openwiden.webhooks import models as webhook_models
from django.utils.translation import gettext_lazy as _
from openwiden.repositories import services


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
        r = self.client.get(f"groups/{organization.remote_id}/members/{self.vcs_account.remote_id}", token=self.token)

        if r.status_code == 200:
            return True, r.json()["access_level"] >= 40
        elif r.status_code == 404:
            return False, False
        else:
            raise exceptions.RemoteSyncException(r.json())

    def repo_webhook_exist(self, repo: repo_models.Repository, webhook_id: int) -> bool:
        r = self.client.get(f"projects/{repo.remote_id}/hooks/{webhook_id}", token=self.token)
        if r.status_code == 200:
            return True
        elif r.status_code == 404:
            return False
        else:
            raise exceptions.RemoteException(_("unexpected error occurred for repository webhook exist check."))

    def update_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        d = dict(
            url=webhook.url,
            issues_events=webhook.issue_events_enabled,
            enable_ssl_verification=True,
            token=webhook.secret,
        )
        r = self.client.put(f"projects/{webhook.repository.remote_id}/hooks", json=d, token=self.token)

        if r.status_code == 200:
            data = r.json()
            webhook.updated_at = data["updated_at"]
            webhook.is_active = True
            webhook.save(update_fields=("updated_at", "is_active"))
        else:
            raise exceptions.RemoteSyncException(_("error occurred on repository webhook create."))

    def create_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        d = dict(
            url=webhook.url,
            issues_events=True,
            enable_ssl_verification=True,
            token=webhook.secret,
        )
        r = self.client.post(f"projects/{webhook.repository.remote_id}/hooks", json=d, token=self.token)

        if r.status_code == 201:
            data = r.json()
            webhook.remote_id = data["id"]
            webhook.created_at = data["created_at"]
            webhook.is_active = True
            webhook.issue_events_enabled = True
            webhook.save(update_fields=("remote_id", "created_at", "is_active", "issue_events_enabled"))
        else:
            raise exceptions.RemoteSyncException(_("error occurred on repository webhook create."))

    def handle_webhook_data(self, webhook: webhook_models.RepositoryWebhook, event: str, data):
        d = data["object_attributes"]

        print(webhook)
        print(event)
        print(d)

        if event == "Issue Hook":

            # d["labels"] = []
            d["web_url"] = d["url"]

            # Fix for datetime formats
            # https://gitlab.com/gitlab-org/gitlab-foss/-/issues/38138
            for k in ("created_at", "updated_at", "closed_at"):
                if k in d and d[k] is not None:
                    d[k] = datetime.strptime(d[k], constants.GITLAB_WEBHOOK_DATETIME_FORMAT)

            serializer = self.issue_sync_serializer(data=d)

            if serializer.is_valid():
                services.Issue.sync(repo=webhook.repository, **serializer.validated_data)
            else:
                raise exceptions.RemoteException("issue webhook handle exception: " + str(serializer.errors))
