import socket

import pytest
from django.contrib.auth.models import AnonymousUser
from faker import Faker
from pytest_django.live_server_helper import LiveServer
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from selenium import webdriver

from openwiden import enums
from openwiden.enums import VersionControlService
from openwiden.users import models as users_models, services as users_services
from openwiden.users.tests import factories as users_factories
from openwiden.organizations.tests import factories as org_factories
from openwiden.webhooks import models as webhook_models
from openwiden.webhooks.tests import factories as webhook_factories
from openwiden.repositories import models as repo_models
from openwiden.repositories.tests import factories as repo_factories


fake = Faker()


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture()
def user() -> users_models.User:
    return users_factories.UserFactory()


@pytest.fixture()
def anonymous_user() -> AnonymousUser:
    return AnonymousUser()


@pytest.fixture()
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


@pytest.fixture()
def create_api_client():
    def _create_api_client(user: users_models.User = None, access_token: str = None) -> APIClient:
        client = APIClient()

        if user:
            access_token = str(RefreshToken.for_user(user).access_token)

        if access_token:
            client.credentials(HTTP_AUTHORIZATION="JWT {access_token}".format(access_token=access_token))

        return client

    return _create_api_client


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


@pytest.fixture
def repository() -> repo_models.Repository:
    return repo_factories.Repository()


@pytest.fixture()
def create_repository():
    def factory(**kwargs) -> repo_models.Repository:
        return repo_factories.Repository(**kwargs)

    return factory


@pytest.fixture()
def random_vcs() -> str:
    return fake.random_element(VersionControlService.values)


@pytest.fixture()
def authlib_settings_github() -> dict:
    return {
        "client_id": "GITHUB_CLIENT_ID",
        "client_secret": "GITHUB_SECRET_KEY",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "access_token_params": None,
        "authorize_url": "https://github.com/login/oauth/authorize",
        "authorize_params": None,
        "api_base_url": "https://api.github.com/",
        "client_kwargs": {"scope": "user:email"},
    }


@pytest.fixture()
def authlib_settings_gitlab() -> dict:
    return {
        "client_id": "GITHUB_CLIENT_ID",
        "client_secret": "GITHUB_SECRET_KEY",
        "access_token_url": "http://gitlab.example.com/oauth/token",
        "access_token_params": None,
        "authorize_url": "https://gitlab.example.com/oauth/authorize",
        "authorize_params": None,
        "api_base_url": "https://gitlab.example.com/api/v4/",
        "client_kwargs": None,
    }


@pytest.fixture()
def selenium():
    with webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub", desired_capabilities=webdriver.DesiredCapabilities.FIREFOX
    ) as driver:
        yield driver


@pytest.fixture(scope="session")
def live_server() -> LiveServer:
    server = LiveServer(socket.gethostbyname(socket.gethostname()))
    yield server
    server.stop()


class MockProfile(users_services.Profile):
    def __init__(self, username: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username

    def json(self):
        return {
            "id": self.id,
            "login": self.login,
            "name": self._name,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "username": self.username,
        }


@pytest.fixture()
def create_mock_profile():
    def _create_mock_profile(
        id=fake.pyint(),
        login=fake.pystr(),
        name=fake.name(),
        email=fake.email(),
        avatar_url=fake.url(),
        split_name=True,
        access_token=fake.pystr(),
        expires_at=fake.pyint(),
        token_type="bearer",
        refresh_token=fake.pystr(),
        username=fake.pystr(),
    ) -> MockProfile:
        return MockProfile(
            id=id,
            login=login,
            name=name,
            email=email,
            avatar_url=avatar_url,
            split_name=split_name,
            access_token=access_token,
            expires_at=expires_at,
            token_type=token_type,
            refresh_token=refresh_token,
            username=username,
        )

    return _create_mock_profile


@pytest.fixture()
def fake_token() -> dict:
    return {
        "access_token": fake.pystr(),
        "expires_at": fake.pyint(),
        "refresh_token": fake.pystr(),
        "token_type": fake.random_element(["bearer", "Bearer", "JWt", "token"]),
    }
