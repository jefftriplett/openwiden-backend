from typing import List

from .models import Repository
from ..abstract import AbstractVCSClient


class GitlabClient(AbstractVCSClient):
    def get_user_repositories(self) -> List[Repository]:
        json = self._get("projects/?membership=True&archived=False&visibility=public")
        return [Repository.from_json(data) for data in json]

    def get_repository(self, repository_id: int) -> Repository:
        json = self._get(f"projects/{repository_id}")
        return Repository.from_json(json)
