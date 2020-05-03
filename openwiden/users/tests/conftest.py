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
