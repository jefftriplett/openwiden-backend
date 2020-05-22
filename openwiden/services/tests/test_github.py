import pytest

from openwiden import exceptions
from openwiden.repositories import models
from openwiden.services.github import GitHubService
from openwiden.services import constants


pytestmark = pytest.mark.django_db


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


class TestWebhook:
    def test_create_webhook(self):
        pass
