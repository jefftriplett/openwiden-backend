from typing import List

from requests import Response

from . import models
from ..abstract import AbstractVCSClient


class GitHubClient(AbstractVCSClient):
    def create_webhook(
        self,
        *,
        owner: str,
        repo: str,
        url: str,
        secret: str,
        events: List[str] = None,
        active: bool = True,
    ) -> models.Webhook:
        """
        Creates repository webhook.

        GitHub docs:
        https://developer.github.com/v3/repos/hooks/#create-a-repository-webhook
        """
        config = {
            "url": url,
            "content_type": "json",
            "secret": secret,
            "insecure_ssl": 0,
        }
        data = {"active": active, "config": config}

        if events:
            data["events"] = events

        url = f"/repos/{owner}/{repo}/hooks"

        json = self._post(url=url, data=data)

        return models.Webhook.from_json(json)
