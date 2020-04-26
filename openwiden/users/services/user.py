from rest_framework_simplejwt.tokens import RefreshToken

from openwiden.users import models
from openwiden.users.services import exceptions


class UserService:
    @staticmethod
    def get_jwt(user: models.User) -> dict:
        """
        Returns JWT tokens for specified user.
        """
        refresh = RefreshToken.for_user(user)
        return dict(access=str(refresh.access_token), refresh=str(refresh))

    @staticmethod
    def get_oauth_token(user: models.User, provider: str) -> models.OAuth2Token:
        """
        Returns oauth token for specified user or provider if it does exist,
        or raises service exception error.
        """
        try:
            oauth_token = models.OAuth2Token.objects.get(user=user, provider=provider)
        except models.OAuth2Token.DoesNotExist:
            raise exceptions.UserServiceException(provider)
        else:
            return oauth_token
