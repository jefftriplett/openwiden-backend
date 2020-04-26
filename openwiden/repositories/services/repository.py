import typing as t

from openwiden.users import models as user_models, services as user_services
from openwiden.repositories.services import serializers
from openwiden import enums

from .abstract import ExternalAPIRepositoryService


class GitHubRepositoryService(ExternalAPIRepositoryService):
    PROVIDER = enums.VersionControlService.GITHUB

    @classmethod
    def get_user_repos_json(cls, oauth_token: user_models.OAuth2Token) -> t.List[dict]:
        client = user_services.OAuthService.get_client(cls.PROVIDER)
        return client.get("user/repos", token=oauth_token.to_token()).json()

    @classmethod
    def get_repository_languages_json(cls, oauth_token: user_models.OAuth2Token, full_name: str) -> dict:
        client = user_services.OAuthService.get_client(cls.PROVIDER)
        return client.get(f"repos/{full_name}/languages", token=oauth_token.to_token()).json()


class GitlabRepositoryService(ExternalAPIRepositoryService):
    PROVIDER = enums.VersionControlService.GITLAB

    @classmethod
    def get_user_repos_json(cls, oauth_token: user_models.OAuth2Token) -> t.List[dict]:
        client = user_services.OAuthService.get_client(cls.PROVIDER)
        return client.get(f"users/{oauth_token.remote_id}/projects", token=oauth_token.to_token()).json()

    @classmethod
    def get_repository_languages_json(cls, oauth_token: user_models.OAuth2Token, repository_id: str) -> dict:
        client = user_services.OAuthService.get_client(cls.PROVIDER)
        return client.get(f"projects/{repository_id}/languages", token=oauth_token.to_token()).json()


class RepositoryService:
    @staticmethod
    def download(oauth_token: user_models.OAuth2Token):
        if oauth_token.provider == enums.VersionControlService.GITHUB:
            repo_data = GitHubRepositoryService.get_user_repos_json(oauth_token)

            for d in repo_data:
                pl_data = GitHubRepositoryService.get_repository_languages_json(oauth_token, d["full_name"])
                d["programming_languages"] = pl_data.keys()
                d["version_control_service"] = oauth_token.provider

            repos = serializers.GitHubRepository(data=repo_data, many=True)
            repos.is_valid(raise_exception=True)
            repos.save()
        elif oauth_token.provider == enums.VersionControlService.GITLAB:
            repo_data = GitlabRepositoryService.get_user_repos_json(oauth_token)

            for d in repo_data:
                pl_data = GitlabRepositoryService.get_repository_languages_json(oauth_token, d["id"])
                d["programming_languages"] = pl_data.keys()
                d["version_control_service"] = oauth_token.provider

            repos = serializers.GitlabRepository(data=repo_data, many=True)
            repos.is_valid(raise_exception=True)
            repos.save()
