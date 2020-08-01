from typing import List

from .models import Repository, Issue, Webhook, Organization
from ..abstract import AbstractVCSClient
from ...enums import OrganizationMembershipType


class GitlabClient(AbstractVCSClient):
    def get_user_repositories(self) -> List[Repository]:
        json = self._get("projects/?membership=True&archived=False&visibility=public")
        return [Repository.from_json(data) for data in json]

    def get_repository(self, repository_id: int) -> Repository:
        json = self._get(f"projects/{repository_id}")
        return Repository.from_json(json)

    def get_repository_programming_languages(self, repository_id: int) -> dict:
        return self._get(f"projects/{repository_id}/languages")

    def get_repository_issues(self, repository_id: int) -> List[Issue]:
        json = self._get(f"projects/{repository_id}/issues?state=opened")
        return [Issue.from_json(data) for data in json]

    def get_organization(self, organization_id: int) -> Organization:
        data = self._get(f"groups/{organization_id}")
        return Organization.from_json(data)

    def check_organization_membership(
        self,
        organization_id: int,
    ) -> OrganizationMembershipType:
        response = self._get(
            f"groups/{organization_id}/members/{self.vcs_account.remote_id}",
            return_response=True,
        )
        response_json = response.json()

        # Check membership
        if response.status_code == 200:
            if response_json["access_level"] >= 40:
                return OrganizationMembershipType.ADMIN
            else:
                return OrganizationMembershipType.MEMBER
        elif response.status_code == 404:
            return OrganizationMembershipType.NOT_A_MEMBER
        else:
            raise ValueError("unexpected status code for memebership check")

    def create_webhook(
        self, *, repository_id: int, webhook_url: str, enable_issues_events: bool = True, secret: str,
    ) -> Webhook:
        data = dict(url=webhook_url, issues_events=enable_issues_events, enable_ssl_verification=True, token=secret,)
        json = self._post(f"projects/{repository_id}/hooks", data)
        return Webhook.from_json(json)

    def delete_repository_webhook(self, repository_id: int, webhook_id: int) -> None:
        self._delete(f"projects/{repository_id}/hooks/{webhook_id}")
