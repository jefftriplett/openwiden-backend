import json
import logging

from django.dispatch import receiver
from github_webhooks import signals as github_signals

from openwiden.repositories import services as repositories_services, models as repositories_models
from . import constants

log = logging.getLogger(__name__)


@receiver(signal=github_signals.issues_signal)
def handle_github_issue_event(payload, **kwargs):
    log.info("issues payload received: {payload}".format(payload=payload))
    payload = json.loads(payload)

    if payload["action"] == constants.IssueEventActions.DELETED:
        repositories_services.delete_by_remote_id(remote_id=payload["issue"]["id"])
    else:
        issue_data = dict(
            remote_id=payload["issue"]["id"],
            title=payload["issue"]["title"],
            description=payload["issue"]["body"],
            state=payload["issue"]["state"],
            labels=[label["name"] for label in payload["issue"]["labels"]],
            url=payload["issue"]["html_url"],
            created_at=payload["issue"]["created_at"],
            closed_at=payload["issue"]["closed_at"],
            updated_at=payload["issue"]["updated_at"],
        )
        try:
            repository = repositories_models.Repository.objects.get(remote_id=payload["repository"]["id"])
        except repositories_models.Repository.DoesNotExist:
            log.info("repository with id {id} not found, abort sync issue.".format(id=payload["repository"]["id"]))
        else:
            repositories_services.sync_issue(repository=repository, **issue_data)
