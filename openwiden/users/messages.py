from django.utils.translation import gettext_lazy as _


VCS_ACCOUNT_DOES_NOT_EXIST = _("You do not have a connected account for {vcs}. Please, try to login again.")
VCS_PROVIDER_NOT_FOUND = _("{vcs} provider is not found.")
AUTHLIB_ERROR = _("An error occurred while trying to connect your account: {error_description}")
INVALID_VCS_ACCOUNT = _("An error occured while trying to save your account data: {serializer_errors}")
