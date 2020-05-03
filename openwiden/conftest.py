import pytest
from rest_framework.test import APIRequestFactory

from openwiden.users import models as users_models
from openwiden.users.tests import factories as users_factories


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> users_models.User:
    return users_factories.UserFactory()


@pytest.fixture
def oauth_token() -> users_models.OAuth2Token:
    return users_factories.OAuth2TokenFactory()


@pytest.fixture
def create_oauth_token():
    def factory(**kwargs) -> users_models.OAuth2Token:
        return users_factories.OAuth2TokenFactory(**kwargs)

    return factory


@pytest.fixture
def api_rf() -> APIRequestFactory:
    return APIRequestFactory()
