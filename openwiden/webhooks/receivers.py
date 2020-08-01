import logging
from datetime import datetime

from django.dispatch import receiver
from github_webhooks import signals as github_signals
from gitlab_webhooks import signals as gitlab_signals

from openwiden.repositories import services as repositories_services
from openwiden.vcs_clients.gitlab import models as gitlab_models
from openwiden.vcs_clients.github import models as github_models
from . import constants

log = logging.getLogger(__name__)


@receiver(github_signals.issues)
def handle_github_issue_event(payload, **kwargs):
    log.info("issues payload received: {payload}".format(payload=payload))

    if payload["action"] in [
        constants.IssueEventActions.OPENED,
        constants.IssueEventActions.CLOSED,
        constants.IssueEventActions.EDITED,
        constants.IssueEventActions.LABELED,
        constants.IssueEventActions.UNLABELED,
    ]:
        payload["issue"]["repository_id"] = payload["repository"]["id"]
        issue = github_models.Issue.from_json(payload["issue"])
        repositories_services.sync_github_repository_issue(issue=issue)
    elif payload["action"] == constants.IssueEventActions.DELETED:
        repositories_services.delete_issue_by_remote_id(remote_id=payload["issue"]["id"])
    else:
        log.info(f"skip issue {payload['action']} action")


@receiver(gitlab_signals.issue)
def handle_gitlab_issue_event(payload: dict, **kwargs) -> None:
    log.info("received Gitlab issue event: {payload}".format(payload=payload))

    data = payload["object_attributes"]
    data["web_url"] = data.pop("url")
    data["project_id"] = payload["project"]["id"]

    # Format datetime strings to datetime
    for dt_key in ("created_at", "updated_at", "closed_at"):
        if dt_key in data and data.get(dt_key) is not None:
            data[dt_key] = datetime.strptime(data[dt_key], "%Y-%m-%d %H:%M:%S %Z")

    issue = gitlab_models.Issue.from_json(data)
    repositories_services.sync_gitlab_repository_issue(issue=issue)
