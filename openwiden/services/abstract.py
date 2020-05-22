import typing as t
from abc import ABC, abstractmethod

from django.utils.translation import gettext_lazy as _

from openwiden.services import serializers, oauth
from openwiden.users import models as users_models
from openwiden.repositories import services as repo_services
from openwiden.repositories import models as repo_models
from openwiden.organizations import services as org_services
from openwiden.organizations import models as org_models
from openwiden.webhooks import services as webhook_services
from openwiden.webhooks import models as webhook_models
from openwiden import exceptions


class RemoteService(ABC):
    """
    Abstract class for all services implementation.
    """

    repo_sync_serializer: t.Type[serializers.RepositorySync] = None
    org_sync_serializer: t.Type[serializers.OrganizationSync] = None
    issue_sync_serializer: t.Type[serializers.IssueSync] = None

    def __init__(self, vcs_account: users_models.VCSAccount):
        if vcs_account:
            self.vcs_account = vcs_account
            self.vcs = vcs_account.vcs
            self.token = self.vcs_account.to_token()
            self.client = oauth.OAuthService.get_client(self.vcs)

    @abstractmethod
    def parse_org_slug(self, repo_data: dict) -> t.Optional[str]:
        """
        Returns repository organization id or None if repository owner is user.
        """
        pass

    @abstractmethod
    def get_user_repos(self) -> t.List[dict]:
        """
        Returns repository data by calling remote API.
        """
        pass

    @abstractmethod
    def get_repo_languages(self, repo: repo_models.Repository) -> dict:
        """
        Returns repository languages data by calling remote API.
        """
        pass

    @abstractmethod
    def get_repo_issues(self, repo: repo_models.Repository) -> t.List[dict]:
        """
        Returns repository issues data by calling remote API.
        """
        pass

    @abstractmethod
    def get_org(self, slug: str) -> dict:
        """
        Returns organization data by slug field.
        GitHub: name.
        Gitlab: id.
        """
        pass

    @abstractmethod
    def check_org_membership(self, organization: org_models.Organization) -> t.Tuple[bool, bool]:
        """
        Checks organization membership for a current user and returns tuple: is_member & is_admin.
        """
        pass

    def sync(self) -> None:
        """
        Synchronizes user's repositories and organizations.
        """
        repositories_data = self.get_user_repos()
        for data in repositories_data:

            # Check if serializer is valid and try to save repository.
            serializer = self.repo_sync_serializer(data=data)
            if serializer.is_valid():
                repository_kwargs = dict(vcs=self.vcs, **serializer.validated_data)

                # Sync organization or just add user as owner
                organization_slug = self.parse_org_slug(data)
                if organization_slug:
                    organization = self.sync_org(slug=organization_slug)
                    repository_kwargs["organization"] = organization
                else:
                    repository_kwargs["owner"] = self.vcs_account

                # Sync repository locally
                repo_services.Repository.sync(**repository_kwargs)
            else:
                raise exceptions.ServiceException(
                    _("an error occurred while synchronizing repository, please, try again.")
                )

    def sync_repo(self, repo: repo_models.Repository):
        """
        Synchronizes repository.
        """
        self.sync_repo_issues(repo)
        self.sync_repo_webhook(repo)
        repo.programming_languages = self.get_repo_languages(repo)
        repo.save(update_fields=("programming_languages", "is_added"))

    def sync_repo_issues(self, repo: repo_models.Repository):
        """
        Synchronizes repository issues.
        """
        issues = self.get_repo_issues(repo)

        if issues:
            serializer = self.issue_sync_serializer(data=issues, many=True)
            if serializer.is_valid():
                for data in serializer.validated_data:
                    repo_services.Issue.sync(repo, **data)
            else:
                raise exceptions.ServiceException(
                    _("an error occurred while synchronizing issues, please, try again. Errors: {e}").format(
                        e=serializer.errors
                    )
                )

    @abstractmethod
    def create_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        pass

    @abstractmethod
    def update_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        pass

    @abstractmethod
    def repo_webhook_exist(self, repo: repo_models.Repository, webhook_id: int) -> bool:
        pass

    def sync_repo_webhook(self, repo: repo_models.Repository):
        """
        Synchronizes repository webhook.
        """
        webhook, created = webhook_services.RepositoryWebhook.get_or_create(repo)
        if created:
            self.create_repo_webhook(webhook)
        else:
            if webhook.remote_id:
                if self.repo_webhook_exist(repo, webhook.remote_id):
                    self.update_repo_webhook(webhook)
            else:
                self.create_repo_webhook(webhook)

    def sync_org(self, *, org: org_models.Organization = None, slug: str = None):
        """
        Synchronizes organization by instance or slug.
        """
        assert org or slug, "organization instance or slug should be specified."

        # Get organization data and pass for validate
        org_data = self.get_org(slug or org.name)
        org_serializer = self.org_sync_serializer(data=org_data)

        if org_serializer.is_valid():
            organization = org_services.Organization.sync(vcs=self.vcs, **org_serializer.validated_data)[0]

            # Sync organization and membership for a current user
            self.sync_org_membership(organization)
        else:
            raise exceptions.ServiceException(
                _("an error occurred while synchronizing organization, please, try again.")
            )

        return organization

    def sync_org_membership(self, organization: org_models.Organization) -> None:
        """
        Synchronizes organization membership for a current user.
        """
        is_member, is_admin = self.check_org_membership(organization)

        if is_member:
            org_services.Member.sync(organization, self.vcs_account, is_admin)
        else:
            org_services.Organization.remove_member(organization, self.vcs_account)

    @abstractmethod
    def handle_webhook_data(self, webhook: webhook_models.RepositoryWebhook, event: str, data):
        pass
