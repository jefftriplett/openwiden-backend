import typing as t
from abc import ABC, abstractmethod
from openwiden.users import models as user_models, services
from openwiden.repositories.services.external import serializers, exceptions


class ExternalAPIRepositoryService(ABC):
    serializer: t.Type[serializers.RepositorySync] = None

    def __init__(self, oauth_token: user_models.OAuth2Token):
        self.oauth_token = oauth_token
        self.token = self.oauth_token.to_token()
        self.client = services.OAuthService.get_client(self.oauth_token.provider)

    @abstractmethod
    def get_repos(self) -> dict:
        """
        Returns repository data by calling external API.
        """
        pass

    @abstractmethod
    def get_repository_languages(self, full_name_or_id: str) -> dict:
        """
        Returns repository languages data by calling external API.
        """
        pass

    def sync(self) -> None:
        """
        Gets repository data from external API and passes it in the serializer for update or save instance.
        """
        data = self.get_repos()
        serializer = self.serializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save(version_control_service=self.oauth_token.provider)
        else:
            raise exceptions.ExternalAPIRepositoryServiceException(str(serializer.errors))
