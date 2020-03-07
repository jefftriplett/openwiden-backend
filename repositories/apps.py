from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RepositoriesConfig(AppConfig):
    name = "repositories"
    label = "repositories"
    verbose_name = _("repositories")
