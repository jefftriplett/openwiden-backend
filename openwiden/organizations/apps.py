from django.utils.translation import gettext_lazy as _

from openwiden.apps import BaseAppConfig


class OrganizationsAppConfig(BaseAppConfig):
    name = "openwiden.organizations"
    label = "organizations"
    verbose_name = _("organizations")
    unique_id = 3
