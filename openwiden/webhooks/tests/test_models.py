import pytest
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db


class TestRepositoryWebhookModel:
    def test_str(self, repo_webhook):
        assert str(repo_webhook) == _("repository webhook for {repo}").format(repo=repo_webhook.repository.name)

    def test_absolute_url(self, repo_webhook):
        assert repo_webhook.get_absolute_url() == reverse("api-v1:repo-webhook-receive", kwargs={"id": repo_webhook.id})
