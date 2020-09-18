from openwiden.exceptions import ServiceException

from . import messages, apps


class WebhookException(ServiceException):
    app_id = apps.WebhooksAppConfig.unique_id


class RepositoryWebhookAlreadyExists(WebhookException):
    error_code = 1
    error_message = messages.REPOSITORY_WEBHOOK_ALREADY_EXISTS
