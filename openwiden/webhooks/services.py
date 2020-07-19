from uuid import uuid4

from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from openwiden import exceptions
from openwiden.webhooks import models
from openwiden.repositories import models as repo_models
from openwiden import vcs_clients


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


def delete_github_repository_webhook(
    *, repository: repo_models.Repository, github_client: vcs_clients.GitHubClient
) -> None:
    try:
        webhook = repository.webhook
    except models.RepositoryWebhook.DoesNotExist:
        pass
    else:
        github_client.delete_webhook(
            owner_name=repository.owner_name, repository_name=repository.name, webhook_id=webhook.remote_id,
        )
        webhook.delete()
