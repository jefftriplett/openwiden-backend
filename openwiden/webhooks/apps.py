from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebhooksAppConfig(AppConfig):
    name = "openwiden.webhooks"
    label = "webhooks"
    verbose_name = _("webhooks")
