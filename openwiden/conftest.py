import pytest
from rest_framework.test import APIRequestFactory

from openwiden import enums
from openwiden.users import models as users_models
from openwiden.users.tests import factories as users_factories
from openwiden.organizations.tests import factories as org_factories
from openwiden.webhooks import models as webhook_models
from openwiden.webhooks.tests import factories as webhook_factories


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> users_models.User:
    return users_factories.UserFactory()


@pytest.fixture
def create_user():
    def factory(**kwargs):
        return users_factories.UserFactory(**kwargs)

    return factory


@pytest.fixture
def vcs_account() -> users_models.VCSAccount:
    return users_factories.VCSAccountFactory()


@pytest.fixture
def create_vcs_account():
    def factory(**kwargs) -> users_models.VCSAccount:
        return users_factories.VCSAccountFactory(**kwargs)

    return factory


@pytest.fixture
def org():
    return org_factories.Organization()


@pytest.fixture
def create_org():
    def factory(**kwargs):
        return org_factories.Organization(**kwargs)

    return factory


@pytest.fixture
def member():
    return org_factories.Member()


@pytest.fixture
def create_member():
    def factory(**kwargs):
        return org_factories.Member(**kwargs)

    return factory


@pytest.fixture
def api_rf() -> APIRequestFactory:
    return APIRequestFactory()


@pytest.fixture
def mock_user() -> "MockUser":
    return MockUser()


@pytest.fixture
def mock_view() -> "MockView":
    return MockView()


@pytest.fixture
def mock_vcs_account() -> "MockVCSAccount":
    return MockVCSAccount()


@pytest.fixture
def mock_remote_service() -> "MockRemoteService":
    return MockRemoteService()


@pytest.fixture
def mock_org() -> "MockOrganization":
    return MockOrganization()


@pytest.fixture
def mock_member() -> "MockMember":
    return MockMember()


class MockVCSAccount:
    pass


class MockUser:
    pass


class MockView:
    pass


class MockRemoteService:
    @staticmethod
    def sync_repo():
        pass


class MockOrganization:
    pass


class MockMember:
    pass


@pytest.fixture()
def repo_webhook() -> webhook_models.RepositoryWebhook:
    return webhook_factories.RepositoryWebhookFactory()


@pytest.fixture()
def create_repo_webhook():
    def f(**kwargs) -> webhook_models.RepositoryWebhook:
        return webhook_factories.RepositoryWebhookFactory(**kwargs)

    return f


@pytest.fixture()
def github_webhook() -> webhook_models.RepositoryWebhook:
    return webhook_factories.RepositoryWebhookFactory(repository__vcs=enums.VersionControlService.GITHUB)
