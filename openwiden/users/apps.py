from django.utils.translation import gettext_lazy as _

from openwiden.apps import BaseAppConfig


class UsersConfig(BaseAppConfig):
    name = "openwiden.users"
    label = "users"
    verbose_name = _("users")
    unique_id = 1

    def ready(self):
        from . import receivers  # noqa: F401
