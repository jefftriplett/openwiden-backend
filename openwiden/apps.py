from django.apps import AppConfig


class BaseAppConfig(AppConfig):
    unique_id = None


class OpenWidenAppConfig(AppConfig):
    name = "openwiden"

    def ready(self) -> None:
        from . import checks  # noqa: F401
