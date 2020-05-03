from openwiden.users import models
from openwiden.services import exceptions
from django.utils.translation import gettext_lazy as _


class OAuthToken:
    @staticmethod
    def get_token(user: models.User, provider: str) -> models.OAuth2Token:
        try:
            oauth_token = models.OAuth2Token.objects.get(user=user, provider=provider)
        except models.OAuth2Token.DoesNotExist:
            raise exceptions.ServiceException(
                _("You do not have a connected account for {provider}. Please, try to login again.").format(
                    provider=provider
                )
            )
        else:
            return oauth_token
