from typing import Tuple
from uuid import uuid4

from django.contrib.sites.models import Site
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from openwiden import exceptions
from openwiden.webhooks import models
from openwiden.repositories import models as repo_models
from openwiden import vcs_clients


class RepositoryWebhook:
    @staticmethod
    def all() -> QuerySet:
        return models.RepositoryWebhook.objects.all()

    @staticmethod
    def get_or_create(repo: repo_models.Repository) -> Tuple[models.RepositoryWebhook, bool]:
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


def create_github_repository_webhook(
    *, repository: repo_models.Repository, github_client: vcs_clients.GitHubClient,
) -> models.RepositoryWebhook:
    if models.RepositoryWebhook.objects.filter(repository=repository).exists():
        raise exceptions.ServiceException(_("repository webhook already exist."))

    webhook = models.RepositoryWebhook.objects.create(
        repository=repository, secret=uuid4().hex, is_active=False, issue_events_enabled=True,
    )

    webhook_url = "https://{domain}{path}".format(
        domain=Site.objects.get_current().domain,
        path=reverse("api-v1:webhooks:github", kwargs={"id": str(webhook.id)}),
    )

    events = ["issues", "repository"]
    github_webhook = github_client.create_webhook(
        owner_name=repository.owner_name,
        repository_name=repository.name,
        url=webhook_url,
        secret=webhook.secret,
        events=events,
    )

    webhook.remote_id = github_webhook.webhook_id
    webhook.created_at = github_webhook.created_at
    webhook.updated_at = github_webhook.updated_at
    webhook.is_active = github_webhook.active
    webhook.url = github_webhook.config.url
    webhook.save(update_fields=("remote_id", "created_at", "updated_at", "is_active", "url",),)

    return webhook
