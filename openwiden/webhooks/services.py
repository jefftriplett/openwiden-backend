from uuid import uuid4

from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils import timezone

from openwiden.enums import VersionControlService
from openwiden.webhooks import models, exceptions
from openwiden.repositories import models as repo_models
from openwiden.users import models as users_models
from openwiden import vcs_clients


def _create_repository_webhook(*, repository: repo_models.Repository) -> models.RepositoryWebhook:
    if models.RepositoryWebhook.objects.filter(repository=repository).exists():
        raise exceptions.RepositoryWebhookAlreadyExists()

    return models.RepositoryWebhook.objects.create(
        repository=repository, secret=uuid4().hex, is_active=False, issue_events_enabled=True,
    )


def _create_github_repository_webhook(
    *, repository: repo_models.Repository, vcs_account: users_models.VCSAccount,
) -> models.RepositoryWebhook:
    webhook = _create_repository_webhook(repository=repository)

    webhook_url = "https://{domain}{path}".format(
        domain=Site.objects.get_current().domain,
        path=reverse("api-v1:webhooks:github", kwargs={"id": str(webhook.id)}),
    )

    events = ["issues", "repository"]
    github_client = vcs_clients.GitHubClient(vcs_account)
    github_webhook = github_client.create_webhook(
        repository_id=repository.remote_id, url=webhook_url, secret=webhook.secret, events=events,
    )

    webhook.remote_id = github_webhook.webhook_id
    webhook.created_at = github_webhook.created_at
    webhook.updated_at = github_webhook.updated_at
    webhook.is_active = github_webhook.active
    webhook.url = github_webhook.config.url
    webhook.save(update_fields=("remote_id", "created_at", "updated_at", "is_active", "url",),)

    return webhook


def _create_gitlab_repository_webhook(
    *, repository: repo_models.Repository, vcs_account: users_models.VCSAccount,
) -> models.RepositoryWebhook:
    webhook = _create_repository_webhook(repository=repository)

    webhook_url = "https://{domain}{path}".format(
        domain=Site.objects.get_current().domain,
        path=reverse("api-v1:webhooks:gitlab", kwargs={"id": str(webhook.id)}),
    )

    gitlab_client = vcs_clients.GitlabClient(vcs_account)
    webhook_data = gitlab_client.create_webhook(
        repository_id=repository.remote_id, webhook_url=webhook_url, enable_issues_events=True, secret=webhook.secret,
    )

    webhook.remote_id = webhook_data.webhook_id
    webhook.created_at = webhook_data.created_at
    webhook.updated_at = timezone.now()
    webhook.is_active = True
    webhook.url = webhook.url
    webhook.save(update_fields=("remote_id", "created_at", "updated_at", "is_active", "url"))

    return webhook


def _delete_github_repository_webhook(
    *, repository: repo_models.Repository, vcs_account: users_models.VCSAccount,
) -> None:
    github_client = vcs_clients.GitHubClient(vcs_account)
    github_client.delete_webhook(
        repository_id=repository.remote_id, webhook_id=repository.webhook.remote_id,
    )
    repository.webhook.delete()


def _delete_gitlab_repository_webhook(
    *, repository: repo_models.Repository, vcs_account: users_models.VCSAccount,
) -> None:
    gitlab_client = vcs_clients.GitlabClient(vcs_account)
    gitlab_client.delete_repository_webhook(
        repository_id=repository.remote_id, webhook_id=repository.webhook.remote_id,
    )
    repository.webhook.delete()


def create_repository_webhook(
    *, repository: repo_models.Repository, vcs_account: users_models.VCSAccount,
) -> models.RepositoryWebhook:
    if vcs_account.vcs == VersionControlService.GITHUB:
        return _create_github_repository_webhook(repository=repository, vcs_account=vcs_account,)
    elif vcs_account.vcs == VersionControlService.GITLAB:
        return _create_gitlab_repository_webhook(repository=repository, vcs_account=vcs_account,)
    else:
        raise ValueError(f"{vcs_account.vcs} is not supported")


def delete_repository_webhook(*, repository: repo_models.Repository, vcs_account: users_models.VCSAccount,) -> None:
    try:
        repository.webhook
    except models.RepositoryWebhook.DoesNotExist:
        raise ValueError(f"webhook already deleted for repository_id {repository.id}")
    else:
        if repository.vcs == VersionControlService.GITHUB:
            _delete_github_repository_webhook(
                repository=repository, vcs_account=vcs_account,
            )
        elif repository.vcs == VersionControlService.GITLAB:
            _delete_gitlab_repository_webhook(
                repository=repository, vcs_account=vcs_account,
            )
        else:
            raise ValueError(f"{vcs_account.vcs} is not supported")
