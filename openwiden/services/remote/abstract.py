import typing as t
from abc import ABC, abstractmethod

from django.utils.translation import gettext_lazy as _

from openwiden.users import models as users_models
from openwiden.organizations import models as organizations_models
from openwiden.services.remote import serializers, exceptions, oauth


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
    def get_repository_organization(self, data: dict) -> t.Optional[organizations_models.Organization]:
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
    def get_repository_languages(self, full_name_or_id: str) -> dict:
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

    def user_repositories_sync(self) -> None:
        """
        Synchronizes user's repositories from remote API.
        """
        repositories_data = self.get_user_repos()
        for data in repositories_data:
            serializer = self.repository_sync_serializer(data=data)

            # Check if serializer is valid and try to save repository.
            if serializer.is_valid():

                # Get repository organization (if exist) and build default kwargs for serializer save call
                organization = self.get_repository_organization(data)
                kwargs = dict(organization=organization, owner=None, version_control_service=self.oauth_token.provider)

                # Organization is None when repository owner is current user
                if organization is None:
                    kwargs["owner"] = self.user

                # Sync specified data (create or update new repository)
                serializer.save(**kwargs)
            else:
                raise exceptions.RemoteSyncException(
                    _("an error occurred while synchronizing repositories, please, try again.")
                )

    def user_organizations_sync(self) -> t.List[organizations_models.Organization]:
        """
        Synchronizes user's organizations from remote API.
        """
        data = self.get_user_organizations()
        serializer = self.organization_sync_serializer(data=data, many=True)
        if serializer.is_valid():
            return serializer.save(version_control_service=self.oauth_token.provider, user=self.user)
        else:
            raise exceptions.RemoteSyncException(
                _("an error occurred while synchronizing organizations, please, try again.")
            )

    def sync(self):
        """
        Synchronizes user's data from remote API.
        """
        self.user_repositories_sync()
        self.user_organizations_sync()
