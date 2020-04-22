from .base import Base


class Development(Base):
    DEBUG = True

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # https://docs.djangoproject.com/en/dev/ref/settings/#internal-ips
    INTERNAL_IPS = ["127.0.0.1"]
