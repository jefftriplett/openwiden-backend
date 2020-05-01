import typing as t

from .abstract import ExternalAPIRepositoryService, serializers


class GitHubRepositoryService(ExternalAPIRepositoryService):
    serializer = serializers.GitHubRepositorySync

    def get_repos(self) -> t.List[dict]:
        return self.client.get("user/repos?visibility=public", token=self.token).json()

    def get_repository_languages(self, full_name: str) -> dict:
        return self.client.get(f"repos/{full_name}/languages", token=self.token).json()
