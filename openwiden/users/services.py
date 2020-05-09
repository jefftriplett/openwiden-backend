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


class VCSAccount:
    @staticmethod
    def find(user: models.User, vcs: str) -> models.VCSAccount:
        """
        Returns version control service account by specified user and vcs name.
        """
        try:
            vcs_account = models.VCSAccount.objects.get(user=user, vcs=vcs)
        except models.VCSAccount.DoesNotExist:
            raise exceptions.ServiceException(error_messages.VCS_ACCOUNT_DOES_NOT_EXIST.format(vcs=vcs))
        else:
            return vcs_account
