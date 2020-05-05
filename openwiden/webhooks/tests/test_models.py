import pytest
from django.utils.translation import gettext_lazy as _


pytestmark = pytest.mark.django_db


class TestRepositoryWebhookModel:
    def test_str(self, repo_webhook):
        assert str(repo_webhook) == _("repository webhook for {repo}").format(repo=repo_webhook.repository.name)
