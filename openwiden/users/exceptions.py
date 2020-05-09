from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class VCSNotFound(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("{vcs} is not supported version control service.")
    default_code = "invalid"

    def __init__(self, vcs: str):
        detail = force_str(self.default_detail).format(vcs=vcs)
        super().__init__(detail)


class GitLabOAuthMissedRedirectURI(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Required redirect_uri query parameter is missing.")
    default_code = "invalid"
