from typing import List

from . import models
from ..abstract import AbstractVCSClient
from ...enums import OrganizationMembershipType


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
        self, repository_id: int, url: str, secret: str, events: List[str] = None, active: bool = True,
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

        url = f"/repositories/{repository_id}/hooks"

        json = self._post(url=url, data=data)

        return models.Webhook.from_json(json)

    def delete_webhook(self, *, repository_id: int, webhook_id: int) -> None:
        url = f"repositories/{repository_id}/hooks/{webhook_id}"
        self._delete(url=url)

    def get_repository_issues(self, repository_id: int, state: str = "open") -> List[models.Issue]:
        json = self._get(url=f"repositories/{repository_id}/issues?state={state}")
        # Note: GitHub's REST API v3 considers every pull request an issue,
        # but not every issue is a pull request. For this reason, "Issues"
        # endpoints may return both issues and pull requests in the response.
        # We can identify pull requests by the pull_request key.
        json = [issue for issue in json if "pull_request" not in issue]
        return [models.Issue.from_json(issue_data) for issue_data in json]

    def get_repository_languages(self, repository_id: int) -> dict:
        json = self._get(url=f"repositories/{repository_id}/languages")
        return convert_lines_count_to_percentages(json)

    def get_repository(self, repository_id: int) -> models.Repository:
        json = self._get(f"repositories/{repository_id}")
        return models.Repository.from_json(json)

    def get_organization(self, organization_id: int) -> models.Organization:
        json = self._get(url=f"organizations/{organization_id}")
        return models.Organization.from_json(json)

    def check_organization_membership(self, organization_id: int) -> OrganizationMembershipType:
        response = self._get(
            f"user/memberships/organizations/{organization_id}",
            return_response=True,
        )
        response_json = response.json()

        # Check response status code and role, if request is success
        if response.status_code == 200:
            if response_json["role"] == OrganizationMembershipType.ADMIN:
                return OrganizationMembershipType.ADMIN
            elif response_json["role"] == OrganizationMembershipType.MEMBER:
                return OrganizationMembershipType.MEMBER
            else:
                raise ValueError(f"unexpected role retrieved: {response_json['role']}")
        elif response.status_code == 404:
            return OrganizationMembershipType.NOT_A_MEMBER
        else:
            raise ValueError("check organization membership failed, please, try again.")

    def get_user_repositories(self) -> List[models.Repository]:
        json = self._get(url="user/repos?affiliation=owner,organization_member&visibility=public")
        return [models.Repository.from_json(data) for data in json]
