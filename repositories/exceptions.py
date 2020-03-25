from django.utils.encoding import force_str
from rest_framework import exceptions, status
from django.utils.translation import gettext_lazy as _

from .models import VersionControlService


class RepositoryURLParse(exceptions.ParseError):
    default_detail = _("{url} is not a valid URL.")

    def __init__(self, url):
        detail = force_str(self.default_detail).format(url=url)
        super().__init__(detail)


class PrivateRepository(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("You cannot add a private repository.")
    default_code = "invalid"


class VersionControlServiceNotFound(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Service for {host} is not found. Available services are: {available_services}.")
    default_code = "invalid"

    def __init__(self, host: str):
        available_services = ", ".join(VersionControlService.objects.values_list("host", flat=True))
        detail = force_str(self.default_detail).format(host=host, available_services=available_services)
        super().__init__(detail)


class RepositoryAlreadyExists(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Repository already exists.")
    default_code = "invalid"
