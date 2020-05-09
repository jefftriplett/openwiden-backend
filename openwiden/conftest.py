import pytest
from rest_framework.test import APIRequestFactory

from openwiden.users import models as users_models
from openwiden.users.tests import factories as users_factories
from openwiden.organizations.tests import factories as org_factories


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> users_models.User:
    return users_factories.UserFactory()


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


class MockUser:
    pass


class MockView:
    pass
