from abc import ABC, abstractmethod
from openwiden.users import models as user_models, services


class ExternalAPIRepositoryService(ABC):
    PROVIDER = None

    @classmethod
    def get_oauth_token(cls, user: user_models.User) -> user_models.OAuth2Token:
        return services.UserService.get_oauth_token(user, cls.PROVIDER)

    @classmethod
    @abstractmethod
    def get_user_repos_json(cls, user: user_models.User) -> dict:
        pass
