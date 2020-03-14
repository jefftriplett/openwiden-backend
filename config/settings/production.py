from .base import Base


class Production(Base):

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
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ["rest_framework.renderers.JSONRenderer"]
