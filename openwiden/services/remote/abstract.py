import typing as t
from abc import ABC, abstractmethod

from django.utils.translation import gettext_lazy as _

from openwiden.services.remote import serializers, exceptions, oauth
from openwiden.users import models as users_models
from openwiden.repositories import services as repositories_services
from openwiden.repositories import models as repositories_models
from openwiden.organizations import services as organizations_services
from openwiden.organizations import models as organizations_models


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
    def parse_organization_id_and_name(self, repository_data: dict) -> t.Optional[t.Tuple[int, str]]:
        """
        Returns repository organization or None if repository owner is user.
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
    def get_user_organizations(self) -> t.List[dict]:
        """
        Returns user's organizations data by calling remote API.
        """
        pass

    def sync(self) -> None:
        """
        Synchronizes user's repositories and organizations for a new created oauth token.
        """
        repositories_data = self.get_user_repos()
        for data in repositories_data:
            # Parse repository data to check repository owner type - organization or user
            # and create or update organization if organization data exist.
            organization_data = self.parse_organization_id_and_name(data)

            # Check if serializer is valid and try to save repository.
            serializer = self.repository_sync_serializer(data=data)
            if serializer.is_valid():
                repository_kwargs = dict(version_control_service=self.provider, **serializer.validated_data)

                # Sync organization with specified data
                if organization_data:
                    remote_id, name = organization_data
                    organization = organizations_services.Organization.sync(
                        version_control_service=self.provider, remote_id=remote_id, name=name,
                    )[0]

                    # Add organization to repository sync kwargs
                    repository_kwargs["organization"] = organization

                    # Add current user to the organization
                    organizations_services.Organization.add_user(organization, self.user)
                else:
                    repository_kwargs["owner"] = self.user

                # Sync repository
                repositories_services.Repository.sync(**repository_kwargs)
            else:
                raise exceptions.RemoteSyncException(
                    _("an error occurred while synchronizing repositories, please, try again.")
                )

    def sync_repository(self, repository: repositories_models.Repository):
        repository.programming_languages = self.get_repository_languages(repository)
        repository.save()

    def sync_organization(self, organization: organizations_models.Organization):
        pass

    # def user_organizations_sync(self) -> None:
    #     """
    #     Synchronizes user's organizations from remote API.
    #     """
    #     organizations_data = self.get_user_organizations()
    #
    #     for data in organizations_data:
    #         serializer = self.organization_sync_serializer(data=data)
    #
    #         # Try to sync organization with validated data
    #         if serializer.is_valid():
    #             organization = organizations_services.Organization.sync(
    #                 version_control_service=self.provider, **serializer.validated_data,
    #             )[0]
    #             organizations_services.Organization.add_user(organization, self.user)
    #         else:
    #             raise exceptions.RemoteSyncException(
    #                 _("an error occurred while synchronizing organizations, please, try again.")
    #             )
