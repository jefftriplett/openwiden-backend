import pytest

from openwiden.webhooks.tests import factories
from openwiden.webhooks import models


@pytest.fixture
def repo_webhook() -> models.RepositoryWebhook:
    return factories.RepositoryWebhookFactory()
