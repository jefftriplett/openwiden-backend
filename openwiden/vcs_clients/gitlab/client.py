from .models import Repository
from ..abstract import AbstractVCSClient


class GitlabClient(AbstractVCSClient):
    def get_user_repositories(self):
        json = self._get("projects/?membership=True&archived=False&visibility=public")
        return [Repository.from_json(data) for data in json]
