from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrganizationsAppConfig(AppConfig):
    name = "openwiden.organizations"
    label = "organizations"
    verbose_name = _("organizations")
