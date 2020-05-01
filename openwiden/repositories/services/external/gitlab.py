import typing as t

from .abstract import ExternalAPIRepositoryService, serializers


class GitlabRepositoryService(ExternalAPIRepositoryService):
    serializer = serializers.GitlabRepositorySync

    def get_repos(self) -> t.List[dict]:
        return self.client.get(f"users/{self.oauth_token.remote_id}/projects", token=self.token).json()

    def get_repository_languages(self, repository_id: str) -> dict:
        return self.client.get(f"projects/{repository_id}/languages", token=self.token).json()
