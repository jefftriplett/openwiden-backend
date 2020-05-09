import pytest

pytestmark = pytest.mark.django_db


def test_vcs_account_to_token(vcs_account):
    assert vcs_account.to_token() == dict(
        access_token=vcs_account.access_token,
        token_type=vcs_account.token_type,
        refresh_token=vcs_account.refresh_token,
        expires_at=vcs_account.expires_at,
    )


def test_vcs_account_str(vcs_account):
    assert str(vcs_account) == vcs_account.access_token
