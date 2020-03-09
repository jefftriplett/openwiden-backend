from .base import Base


class Development(Base):
    DEBUG = True

    # Apps
    INSTALLED_APPS = Base.INSTALLED_APPS
    INSTALLED_APPS += ("django_nose",)
    TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
    NOSE_ARGS = [
        Base.ROOT_DIR.root,
        "-s",
        "--nologcapture",
        "--with-coverage",
        "--with-progressive",
        "--cover-package=openwiden,users,repositories",
        "--cover-html",
    ]

    # Mail
    EMAIL_HOST = "localhost"
    EMAIL_PORT = 1025
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    # https://docs.djangoproject.com/en/dev/ref/settings/#internal-ips
    INTERNAL_IPS = ["127.0.0.1"]

    # Check if we are inside a Docker container
    if Base.env.bool("USING_DOCKER", False):
        import socket

        # Add the container IP to INTERNAL_IPS
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
