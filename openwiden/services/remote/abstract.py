import typing as t
from abc import ABC, abstractmethod

from django.utils.translation import gettext_lazy as _

from openwiden.users import models as user_models
from openwiden.services.remote import serializers, exceptions, oauth


class RemoteService(ABC):
    """
    Abstract class for all services implementation.
    """

    repository_sync_serializer: t.Type[serializers.RepositorySync] = None

    def __init__(self, oauth_token: user_models.OAuth2Token):
        self.oauth_token = oauth_token
        self.provider = oauth_token.provider
        self.token = self.oauth_token.to_token()
        self.user = self.oauth_token.user
        self.client = oauth.OAuthService.get_client(self.provider)

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

    def user_repositories_sync(self) -> None:
        """
        Synchronizes user's repositories from remote API.
        """
        data = self.get_user_repos()

        serializer = self.repository_sync_serializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save(version_control_service=self.oauth_token.provider, owner=self.user)
        else:
            raise exceptions.RemoteSyncException(
                _("an error occurred while synchronizing repositories, please, try again.")
            )

    def user_organizations_sync(self):
        """
        Synchronizes user's organizations from remote API.
        """
        pass

    def organization_repositories_sync(self) -> None:
        """
        Synchronizes organization's repositories from remote API.
        """
        pass

    def sync(self):
        """
        Synchronizes full user's data from remote API.
        """
        self.user_repositories_sync()
        self.user_organizations_sync()
        self.organization_repositories_sync()
