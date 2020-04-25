from rest_framework_simplejwt.tokens import RefreshToken

from openwiden.users import models


class UserService:
    @staticmethod
    def get_jwt(user: models.User) -> dict:
        """
        Returns JWT tokens for specified user.
        """
        refresh = RefreshToken.for_user(user)
        return dict(access=str(refresh.access_token), refresh=str(refresh))
