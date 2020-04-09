import openwiden
from .base import Base
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


class Production(Base):
    INSTALLED_APPS = Base.INSTALLED_APPS

    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ("gunicorn",)

    # SSL: https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
    SECURE_SSL_REDIRECT = Base.env("DJANGO_SECURE_SSL_REDIRECT", default=False)
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Static files (CSS, JavaScript, Images)
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

    # DRF
    REST_FRAMEWORK = Base.REST_FRAMEWORK
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = ("rest_framework_simplejwt.authentication.JWTAuthentication",)

    # Sentry
    SENTRY_DSN = Base.env("SENTRY_DSN")
    SENTRY_INTEGRATIONS = [DjangoIntegration()]
    SENTRY_SEND_DEFAULT_PII = True
    SENTRY_RELEASE = f"openwiden-backend@{openwiden.__version__}"
    SENTRY_ENVIRONMENT = "production"
    SENTRY_DEBUG = False

    def __init__(self, *args, **kwargs):
        super().__init__()
        sentry_sdk.init(
            dsn=self.SENTRY_DSN,
            integrations=self.SENTRY_INTEGRATIONS,
            send_default_pii=self.SENTRY_SEND_DEFAULT_PII,
            release=self.SENTRY_RELEASE,
            environment=self.SENTRY_ENVIRONMENT,
            debug=self.SENTRY_DEBUG,
        )
