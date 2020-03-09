from django.utils.encoding import force_str
from rest_framework import exceptions, status
from django.utils.translation import gettext_lazy as _


class RepositoryURLParse(exceptions.ParseError):
    default_detail = _("{url} is not a valid URL.")

    def __init__(self, url):
        detail = force_str(self.default_detail).format(url=url)
        super().__init__(detail)


class PrivateRepository(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("You cannot add a private repository.")
    default_code = "invalid"
