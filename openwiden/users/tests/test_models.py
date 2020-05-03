import pytest

pytestmark = pytest.mark.django_db


def test_oauth_token_to_token(oauth_token):
    assert oauth_token.to_token() == dict(
        access_token=oauth_token.access_token,
        token_type=oauth_token.token_type,
        refresh_token=oauth_token.refresh_token,
        expires_at=oauth_token.expires_at,
    )


def test_oauth_token_str(oauth_token):
    assert str(oauth_token) == oauth_token.access_token
