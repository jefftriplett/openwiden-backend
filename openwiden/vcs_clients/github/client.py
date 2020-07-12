from typing import List

from . import models
from ..abstract import AbstractVCSClient


def convert_lines_count_to_percentages(repository_languages: dict) -> dict:
    """
    Converts repo languages lines count into percentages.
    """
    total_lines_count = sum(repository_languages.values())
    for k, v in repository_languages.items():
        repository_languages[k] = round(v / total_lines_count * 100, 2)
    return repository_languages


class GitHubClient(AbstractVCSClient):
    def create_webhook(
        self,
        *,
        owner_name: str,
        repository_name: str,
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

        url = f"/repos/{owner_name}/{repository_name}/hooks"

        json = self._post(url=url, data=data)

        return models.Webhook.from_json(json)

    def get_repository_issues(
        self,
        *,
        owner_name: str,
        repository_name: str,
        state: str = "open"
    ) -> List[models.Issue]:
        json = self._get(url=f"repos/{owner_name}/{repository_name}/issues?state={state}")
        # Note: GitHub's REST API v3 considers every pull request an issue,
        # but not every issue is a pull request. For this reason, "Issues"
        # endpoints may return both issues and pull requests in the response.
        # We can identify pull requests by the pull_request key.
        json = [issue for issue in json if "pull_request" not in issue]
        return [models.Issue.from_json(issue_data) for issue_data in json]

    def get_repository_languages(self, *, owner_name: str, repository_name: str) -> dict:
        json = self._get(url=f"repos/{owner_name}/{repository_name}/languages")
        return convert_lines_count_to_percentages(json)

    def get_repository(
        self,
        *,
        owner_name: str = None,
        repository_name: str = None,
        repository_id: int = None,
    ) -> models.Repository:
        if owner_name and repository_name:
            url = f"repos/{owner_name}/{repository_name}"
        elif repository_id:
            url = f"repositories/{repository_id}"
        else:
            msg = "owner_name and repository_name OR repository_id should be specified"
            raise ValueError(msg)

        json = self._get(url=url)
        return models.Repository.from_json(json)

    def get_organization(self, organization_name: str) -> models.Organization:
        json = self._get(url=f"orgs/{organization_name}")
        return models.Organization.from_json(json)

    def check_organization_membership(
        self, organization_name: str,
    ) -> models.MembershipType:
        url = f"/user/memberships/orgs/{organization_name}"
        response = self._client.get(url, token=self.vcs_account.to_token())
        json = response.json()

        if response.status_code == 200:
            if json["role"] == models.MembershipType.ADMIN:
                return models.MembershipType.ADMIN
            elif json["role"] == models.MembershipType.MEMBER:
                return models.MembershipType.MEMBER
            else:
                raise ValueError(f"unexpected role retrieved: {json['role']}")
        elif response.status_code == 404:
            return models.MembershipType.NOT_A_MEMBER
        else:
            raise ValueError("check organization membership failed, please, try again.")
