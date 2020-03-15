from openwiden import get_version
from .base import Base
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


class Production(Base):

    DEBUG = Base.DEBUG
    INSTALLED_APPS = Base.INSTALLED_APPS

    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ("gunicorn",)

    # SSL: https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Static files (CSS, JavaScript, Images)
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    REST_FRAMEWORK = Base.REST_FRAMEWORK

    SENTRY_INIT_KWARGS = {
        "dsn": Base.env("SENTRY_DSN"),
        "integrations": [DjangoIntegration()],
        "send_default_pii": True,
    }
    DEFAULT_RENDERER_CLASSES = ("rest_framework.renderers.JSONRenderer",)

    if DEBUG:
        DEFAULT_RENDERER_CLASSES += ("rest_framework.renderers.BrowsableAPIRenderer",)
        SENTRY_INIT_KWARGS.update(
            {"debug": True, "environment": "staging",}
        )
    else:
        SENTRY_INIT_KWARGS.update(
            {"release": f"openwiden-backend@{get_version()}", "environment": "production",}
        )

    sentry_sdk.init(**SENTRY_INIT_KWARGS)

    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = DEFAULT_RENDERER_CLASSES
