import pytest
from django.contrib.sites.models import Site

from openwiden.webhooks import services, models

pytestmark = pytest.mark.django_db


class TestWebhookService:
    def test_all(self, create_repo_webhook):
        repo_webhook = create_repo_webhook()
        qs = services.RepositoryWebhook.all()
        expected_qs = models.RepositoryWebhook.objects.all()

        assert qs.count() == expected_qs.count()
        assert qs.first().id == repo_webhook.id
        assert expected_qs.first().id == repo_webhook.id

    def test_get_or_create_returns_repo_webhook(self, repo_webhook):
        assert services.RepositoryWebhook.get_or_create(repo_webhook.repository) == (repo_webhook, False)

    def test_get_or_create_creates_new_webhook(self, repository, monkeypatch):
        domain, absolute_url = "example.com", "/fake-url/"

        def mock_get_current():
            class MockSite:
                @property
                def domain(self):
                    return domain

            return MockSite()

        def mock_get_absolute_url(*args):
            return absolute_url

        monkeypatch.setattr(Site.objects, "get_current", mock_get_current)
        monkeypatch.setattr(models.RepositoryWebhook, "get_absolute_url", mock_get_absolute_url)
        expected_url = "https://{domain}{absolute_url}".format(domain=domain, absolute_url=absolute_url)

        assert models.RepositoryWebhook.objects.filter(repository=repository).exists() is False

        webhook, created = services.RepositoryWebhook.get_or_create(repository)

        assert webhook.url == expected_url
        assert created is True
