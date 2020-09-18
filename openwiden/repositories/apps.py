from django.utils.translation import gettext_lazy as _

from openwiden.apps import BaseAppConfig


class RepositoriesConfig(BaseAppConfig):
    name = "openwiden.repositories"
    label = "repositories"
    verbose_name = _("repositories")
    unique_id = 2
