from .production import Production


class Staging(Production):

    # DRF
    REST_FRAMEWORK = Production.REST_FRAMEWORK
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.JSONRenderer",
    )

    # Sentry
    SENTRY_RELEASE = None
    SENTRY_ENVIRONMENT = "staging"
    SENTRY_DEBUG = True
