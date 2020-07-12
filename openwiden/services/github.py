import typing as t

from .serializers import GitHubRepositorySync, GithubOrganizationSync, GitHubIssueSync


class GitHubService:
    repo_sync_serializer = GitHubRepositorySync
    org_sync_serializer = GithubOrganizationSync
    issue_sync_serializer = GitHubIssueSync

    def get_user_repos(self) -> t.List[dict]:
        repositories = self.client.get(
            "user/repos?affiliation=owner,organization_member&visibility=public", token=self.token
        ).json()
        return [repo for repo in repositories if repo["archived"] is False]
