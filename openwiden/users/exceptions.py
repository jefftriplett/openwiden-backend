from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _

from openwiden.exceptions import ServiceException

from . import messages, apps


class GitLabOAuthMissedRedirectURI(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Required redirect_uri query parameter is missing.")
    default_code = "invalid"


class UserException(ServiceException):
    app_id = apps.UsersConfig.unique_id


class VCSProviderNotFound(UserException):
    error_code = 1
    error_message = messages.VCS_PROVIDER_NOT_FOUND


class AuthlibError(UserException):
    error_code = 2
    error_message = messages.AUTHLIB_ERROR


class InvalidVCSAccount(UserException):
    error_code = 3
    error_message = messages.INVALID_VCS_ACCOUNT


class VCSAccountDoesNotExist(UserException):
    error_code = 4
    error_message = messages.VCS_ACCOUNT_DOES_NOT_EXIST
