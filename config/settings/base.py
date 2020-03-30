import environ
from datetime import timedelta

from configurations import Configuration


class Base(Configuration):
    # Path configurations
    # /openwiden/settings/base.py - 3 = /
    ROOT_DIR = environ.Path(__file__) - 3

    # Environment
    env = environ.Env()

    # Apps
    DJANGO_APPS = (
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.postgres",
    )
    THIRD_PARTY_APPS = (
        "rest_framework",
        "django_filters",
        "drf_yasg",
        "corsheaders",
        "django_q",
    )
    LOCAL_APPS = (
        "users",
        "repositories",
    )

    # https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
    INSTALLED_APPS = ("whitenoise.runserver_nostatic",) + INSTALLED_APPS

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    )

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = env.bool("DJANGO_DEBUG", default=False)

    # https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
    SECRET_KEY = env("DJANGO_SECRET_KEY")

    ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])
    ROOT_URLCONF = "config.urls"
    WSGI_APPLICATION = "config.wsgi.application"
    APPEND_SLASH = True
    TIME_ZONE = "UTC"
    LANGUAGE_CODE = "en-us"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = "/"
    SITE_ID = 1
    ADMINS = (("Author", "stefanitsky.mozdor@gmail.com"),)

    # Email
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    # Postgres
    DATABASES = {"default": env.db(default="postgresql://postgres:@db:5432/postgres")}

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = str(ROOT_DIR.path("staticfiles"))
    STATICFILES_DIRS = []
    STATIC_URL = "/static/"
    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    )

    # Media files
    MEDIA_ROOT = str(ROOT_DIR.path("media"))
    MEDIA_URL = "/media/"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # Custom user model
    AUTH_USER_MODEL = "users.User"

    # Auth backends
    AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

    # Django Rest Framework
    REST_FRAMEWORK = {
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": int(env("DJANGO_PAGINATION_LIMIT", default=10)),
        "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
        "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema",
        "DEFAULT_RENDERER_CLASSES": (
            "rest_framework.renderers.BrowsableAPIRenderer",
            "rest_framework.renderers.JSONRenderer",
        ),
        "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ),
    }

    GITHUB_CLIENT_ID = env("GITHUB_CLIENT_ID")
    GITHUB_SECRET_KEY = env("GITHUB_SECRET_KEY")

    GITLAB_APP_ID = env("GITLAB_APP_ID")
    GITLAB_SECRET = env("GITLAB_SECRET")
    GITLAB_DEFAULT_REDIRECT_URI = env(
        "GITLAB_DEFAULT_REDIRECT_URI", default="http://0.0.0.0:8000/users/complete/gitlab/"
    )

    AUTHLIB_OAUTH_CLIENTS = {
        "github": {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_SECRET_KEY,
            "access_token_url": "https://github.com/login/oauth/access_token",
            "access_token_params": None,
            "authorize_url": "https://github.com/login/oauth/authorize",
            "authorize_params": None,
            "api_base_url": "https://api.github.com/",
            "client_kwargs": {"scope": "user:email"},
        },
        "gitlab": {
            "client_id": GITLAB_APP_ID,
            "client_secret": GITLAB_SECRET,
            "access_token_url": "https://gitlab.com/oauth/token",
            "access_token_params": None,
            "authorize_url": "https://gitlab.com/oauth/authorize",
            "authorize_params": {"redirect_uri": GITLAB_DEFAULT_REDIRECT_URI},
            "api_base_url": "https://gitlab.com/api/v4/",
            "client_kwargs": None,
        },
    }

    # JWT
    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
        "AUTH_HEADER_TYPES": ("JWT",),
    }

    # Swagger
    SWAGGER_SETTINGS = {
        "USE_SESSION_AUTH": False,
        "SECURITY_DEFINITIONS": {"JWT": {"type": "apiKey", "name": "Authorization", "in": "header"},},
    }

    # Cors headers
    CORS_ORIGIN_ALLOW_ALL = True

    Q_CLUSTER = {
        "name": "openwiden",
        "workers": 8,
        "recycle": 500,
        "timeout": 60,
        "compress": True,
        "save_limit": 250,
        "queue_limit": 500,
        "cpu_affinity": 1,
        "label": "Django Q",
        "redis": {"host": "cache", "port": 6379, "db": 0,},
    }
