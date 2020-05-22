from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "openwiden.users"
    label = "users"
    verbose_name = _("users")

    def ready(self):
        from . import signals  # noqa: F401
