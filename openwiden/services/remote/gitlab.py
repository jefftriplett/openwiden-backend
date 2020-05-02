import typing as t

from .abstract import RemoteService
from .serializers import GitlabRepositorySync


class GitlabService(RemoteService):
    repository_sync_serializer = GitlabRepositorySync

    def get_user_repos(self) -> t.List[dict]:
        # TODO: pagination
        return self.client.get(f"users/{self.oauth_token.remote_id}/projects", token=self.token).json()

    def get_repository_languages(self, repository_id: str) -> dict:
        return self.client.get(f"projects/{repository_id}/languages", token=self.token).json()
