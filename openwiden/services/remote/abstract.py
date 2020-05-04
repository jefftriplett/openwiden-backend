import typing as t
from abc import ABC, abstractmethod

from django.utils.translation import gettext_lazy as _

from openwiden.services.remote import serializers, exceptions, oauth
from openwiden.users import models as users_models
from openwiden.repositories import services as repositories_services
from openwiden.repositories import models as repositories_models
from openwiden.organizations import services as org_services
from openwiden.organizations import models as org_models


class RemoteService(ABC):
    """
    Abstract class for all services implementation.
    """

    repository_sync_serializer: t.Type[serializers.RepositorySync] = None
    organization_sync_serializer: t.Type[serializers.OrganizationSync] = None

    def __init__(self, oauth_token: users_models.OAuth2Token):
        self.oauth_token = oauth_token
        self.provider = oauth_token.provider
        self.token = self.oauth_token.to_token()
        self.user = self.oauth_token.user
        self.client = oauth.OAuthService.get_client(self.provider)

    @abstractmethod
    def parse_organization_slug(self, repository_data: dict) -> t.Optional[str]:
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
    def get_repository_languages(self, repository: repositories_models.Repository) -> dict:
        """
        Returns repository languages data by calling remote API.
        """
        pass

    @abstractmethod
    def get_organization(self, slug: str) -> dict:
        pass

    @abstractmethod
    def check_org_membership(self, organization: org_models.Organization) -> t.Tuple[bool, bool]:
        pass

    def sync(self) -> None:
        """
        Synchronizes user's repositories and organizations for a new created oauth token.
        """
        repositories_data = self.get_user_repos()
        for data in repositories_data:

            # Check if serializer is valid and try to save repository.
            serializer = self.repository_sync_serializer(data=data)
            if serializer.is_valid():
                repository_kwargs = dict(version_control_service=self.provider, **serializer.validated_data)

                # Sync organization or just add user as owner
                organization_slug = self.parse_organization_slug(data)
                if organization_slug:
                    organization = self.sync_org(slug=organization_slug)
                    repository_kwargs["organization"] = organization
                else:
                    repository_kwargs["owner"] = self.user

                # Sync repository
                repositories_services.Repository.sync(**repository_kwargs)
            else:
                raise exceptions.RemoteSyncException(
                    _("an error occurred while synchronizing repository, please, try again.")
                )

    def sync_repository(self, repository: repositories_models.Repository):
        repository.programming_languages = self.get_repository_languages(repository)
        repository.save(update_fields=("programming_languages", "is_added",))

    def sync_org(self, *, org: org_models.Organization = None, slug: str = None):
        """
        Synchronizes organization by instance or slug.
        """
        assert org or slug, "organization instance or slug should be specified."

        # Get organization data and pass for validate
        org_data = self.get_organization(slug or org.name)
        org_serializer = self.organization_sync_serializer(data=org_data)

        if org_serializer.is_valid():
            organization = org_services.Organization.sync(
                version_control_service=self.provider, **org_serializer.validated_data
            )[0]
            # Sync organization and membership for a current user
            self.sync_organization_membership(organization)
        else:
            raise exceptions.RemoteSyncException(
                _("an error occurred while synchronizing organization, please, try again.")
            )

        return organization

    def sync_organization_membership(self, organization: org_models.Organization) -> None:
        """
        Synchronizes organization membership for a current user.
        """
        is_member, is_admin = self.check_org_membership(organization)

        if is_member:
            org_services.Organization.sync_member(organization, self.user, is_admin)
        else:
            org_services.Organization.remove_member(organization, self.user)
