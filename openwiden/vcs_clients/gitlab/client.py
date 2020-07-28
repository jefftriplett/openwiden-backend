from typing import List

from .models import Repository, Issue, Webhook
from ..abstract import AbstractVCSClient


class GitlabClient(AbstractVCSClient):
    def get_user_repositories(self) -> List[Repository]:
        json = self._get("projects/?membership=True&archived=False&visibility=public")
        return [Repository.from_json(data) for data in json]

    def get_repository(self, repository_id: int) -> Repository:
        json = self._get(f"projects/{repository_id}")
        return Repository.from_json(json)

    def get_repository_programming_languages(self, repository_id: int) -> dict:
        return self._get(f"projects/{repository_id}/languages")

    def get_repository_issues(self, repository_id: int) -> List[Issue]:
        json = self._get(f"projects/{repository_id}/issues?state=opened")
        return [Issue.from_json(data) for data in json]

    def create_webhook(
        self, *, repository_id: int, webhook_url: str, enable_issues_events: bool = True, secret: str,
    ) -> Webhook:
        data = dict(url=webhook_url, issues_events=enable_issues_events, enable_ssl_verification=True, token=secret,)
        json = self._post(f"projects/{repository_id}/hooks", data)
        return Webhook.from_json(json)

    def delete_repository_webhook(self, repository_id: int, webhook_id: int) -> None:
        self._delete(f"projects/{repository_id}/hooks/{webhook_id}")
