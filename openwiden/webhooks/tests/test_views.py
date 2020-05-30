import pytest
from django.http import Http404

from openwiden.webhooks import views


pytestmark = pytest.mark.django_db


class TestRepositoryWebhookView:
    view = views.RepositoryWebhookView()

    def test_repository_webhook_view_not_found(self, api_rf):
        request = api_rf.post("/fake-url/")

        with pytest.raises(Http404):
            self.view.post(request, "12345")

    def test_repository_webhook_view_success(self, api_rf, repo_webhook, monkeypatch):
        expected_response = {}

        def return_mock_service(*args, **kwargs):
            class MockService:
                def handle_webhook(self, *args, **kwargs):
                    return expected_response

            return MockService()

        monkeypatch.setattr(views, "get_service", return_mock_service)
        request = api_rf.post("/fake-url/")

        assert self.view.post(request, repo_webhook.id) == expected_response
