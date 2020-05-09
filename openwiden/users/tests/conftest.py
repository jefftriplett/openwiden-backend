import pytest


@pytest.fixture
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


@pytest.fixture
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


@pytest.fixture
def mock_user() -> "MockUser":
    return MockUser()


@pytest.fixture
def mock_vcs_account() -> "MockVCSAccount":
    return MockVCSAccount()


@pytest.fixture
def create_mock_refresh_token():
    def factory(access: str, refresh: str) -> MockRefreshToken:
        return MockRefreshToken(access=access, refresh=refresh)

    return factory


@pytest.fixture
def mock_view() -> "MockView":
    return MockView()


class MockUser:
    pass


class MockVCSAccount:
    pass


class MockRefreshToken:
    def __init__(self, access: str, refresh: str):
        self.access_token = access
        self.refresh = refresh

    def __str__(self):
        return self.refresh


class MockView:
    pass
