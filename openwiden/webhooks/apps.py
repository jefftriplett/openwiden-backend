from django.utils.translation import gettext_lazy as _

from openwiden.apps import BaseAppConfig


class WebhooksAppConfig(BaseAppConfig):
    name = "openwiden.webhooks"
    label = "webhooks"
    verbose_name = _("webhooks")
    unique_id = 4

    def ready(self) -> None:
        from . import receivers  # noqa: F401
