from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class OAuthProviderNotFound(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("{provider} is not supported provider.")
    default_code = "invalid"

    def __init__(self, provider: str):
        detail = force_str(self.default_detail).format(provider=provider)
        super().__init__(detail)


class GitLabOAuthMissedRedirectURI(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Required redirect_uri query parameter is missing.")
    default_code = "invalid"
