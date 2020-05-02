import typing as t

from .abstract import RemoteService
from .serializers import GitHubRepositorySync


class GitHubService(RemoteService):
    repository_sync_serializer = GitHubRepositorySync

    def get_user_repos(self) -> t.List[dict]:
        # TODO: pagination
        return self.client.get("user/repos", token=self.token).json()

    def get_repository_languages(self, full_name: str) -> dict:
        return self.client.get(f"repos/{full_name}/languages", token=self.token).json()
