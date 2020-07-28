from django.db.models import QuerySet

from . import models


def get_webhooks() -> "QuerySet[models.RepositoryWebhook]":
    return models.RepositoryWebhook.objects.all()
