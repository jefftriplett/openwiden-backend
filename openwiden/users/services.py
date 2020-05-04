from rest_framework_simplejwt.tokens import RefreshToken

from openwiden.users import models, error_messages
from openwiden.services import exceptions


class UserService:
    @staticmethod
    def get_jwt(user: models.User) -> dict:
        """
        Returns JWT tokens for specified user.
        """
        refresh = RefreshToken.for_user(user)
        return dict(access=str(refresh.access_token), refresh=str(refresh))


class OAuthToken:
    @staticmethod
    def get_token(user: models.User, provider: str) -> models.OAuth2Token:
        try:
            oauth_token = models.OAuth2Token.objects.get(user=user, provider=provider)
        except models.OAuth2Token.DoesNotExist:
            raise exceptions.ServiceException(error_messages.OAUTH_TOKEN_DOES_NOT_EXIST.format(provider=provider))
        else:
            return oauth_token
