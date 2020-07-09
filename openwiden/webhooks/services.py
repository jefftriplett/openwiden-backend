import typing as t

from uuid import uuid4

from django.contrib.sites.models import Site
from django.db.models import QuerySet

from openwiden.webhooks import models
from openwiden.repositories import models as repo_models


class RepositoryWebhook:
    @staticmethod
    def all() -> QuerySet:
        return models.RepositoryWebhook.objects.all()

    @staticmethod
    def get_or_create(repo: repo_models.Repository) -> t.Tuple[models.RepositoryWebhook, bool]:
        """
        Creates or returns webhook.
        """
        try:
            return repo.webhook, False
        except models.RepositoryWebhook.DoesNotExist:
            webhook = models.RepositoryWebhook.objects.create(
                repository=repo, secret=uuid4().hex, is_active=False, issue_events_enabled=False,
            )

            # Build & set url
            webhook.url = "https://{domain}{absolute_url}".format(
                domain=Site.objects.get_current().domain, absolute_url=webhook.get_absolute_url()
            )
            webhook.save(update_fields=("url",))

            # Return new created webhook
            return webhook, True


def get_webhooks() -> "QuerySet[models.RepositoryWebhook]":
    return models.RepositoryWebhook.objects.all()
