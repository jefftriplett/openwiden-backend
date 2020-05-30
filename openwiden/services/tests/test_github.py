import pytest

from openwiden import exceptions
from openwiden.repositories import models
from openwiden.services.github import GitHubService, convert_lines_count_to_percent
from openwiden.services import constants

pytestmark = pytest.mark.django_db

test_lines_count_data = [
    ({"Python": 300, "JavaScript": 700}, {"Python": 30, "JavaScript": 70}),
    ({"C++": 1100, "C": 28900, "Python": 70000}, {"C++": 1.1, "C": 28.9, "Python": 70}),
]


@pytest.mark.parametrize("lines_count,expected", test_lines_count_data)
def test_convert_lines_count_to_percent(lines_count, expected):
    assert convert_lines_count_to_percent(lines_count) == expected


def test_get_repo_owner(create_repository, org, vcs_account):
    org_repo = create_repository(owner=None, organization=org)
    owner_repo = create_repository(organization=None)
    service = GitHubService(vcs_account=vcs_account)

    assert service.get_repo_owner(org_repo) == org_repo.organization.name
    assert service.get_repo_owner(owner_repo) == vcs_account.login


def test_get_user_repos(vcs_account, monkeypatch):
    class MockResponse:
        def json(self):
            return [{"id": 1, "archived": False}, {"id": 2, "archived": True}]

    class MockClient:
        def get(self, *args, **kwargs):
            return MockResponse()

    def get_mock_client(vcs: str):
        return MockClient()

    monkeypatch.setattr(GitHubService, "get_client", get_mock_client)
    service = GitHubService(vcs_account=vcs_account)

    assert service.get_user_repos() == [{"id": 1, "archived": False}]


class TestHandleWebhook:
    def test_raises_signature_header_is_missing(self, github_webhook, create_request):
        request = create_request(signature=None)

        with pytest.raises(exceptions.ServiceException) as e:
            GitHubService.handle_webhook(github_webhook, request)

        assert e.value.args[0] == constants.Messages.X_HUB_SIGNATURE_HEADER_IS_MISSING

    def test_raises_event_header_is_missing(self, github_webhook, create_request):
        request = create_request(event=None)

        with pytest.raises(exceptions.ServiceException) as e:
            GitHubService.handle_webhook(github_webhook, request)

        assert e.value.args[0] == constants.Messages.X_GITHUB_EVENT_HEADER_IS_MISSING

    def test_raises_digest_is_not_supported(self, github_webhook, create_request):
        request = create_request(signature="test=12345")

        with pytest.raises(exceptions.ServiceException) as e:
            GitHubService.handle_webhook(github_webhook, request)

        assert e.value.args[0] == constants.Messages.DIGEST_IS_NOT_SUPPORTED.format(digest_name="test")

    def test_raises_signature_is_invalid(self, github_webhook, create_request, monkeypatch):
        monkeypatch.setattr(GitHubService, "_compare_signatures", lambda a, b, c: False)
        request = create_request()

        with pytest.raises(exceptions.ServiceException) as e:
            GitHubService.handle_webhook(github_webhook, request)

        assert e.value.args[0] == constants.Messages.X_HUB_SIGNATURE_IS_INVALID

    def test_issue_webhook(self, github_webhook, create_request, mock_issue_edit_data, monkeypatch):
        monkeypatch.setattr(GitHubService, "_compare_signatures", lambda a, b, c: True)
        request = create_request(event=constants.Events.ISSUES)
        request.data = mock_issue_edit_data
        GitHubService.handle_webhook(github_webhook, request)

        assert models.Issue.objects.filter(remote_id=mock_issue_edit_data["issue"]["id"]).exists() is True
