from unittest import mock

import pytest
from authlib.integrations.django_client import DjangoRemoteApp

from openwiden.exceptions import ServiceException
from openwiden.users import services

pytestmark = pytest.mark.django_db


@mock.patch.object(services.RefreshToken, "for_user")
def get_jwt_tokens(patched_refresh_token_for_user, mock_user, create_mock_refresh_token):
    expected = dict(access="12345", refresh="67890")

    patched_refresh_token_for_user.return_value = create_mock_refresh_token(**expected)

    assert services.get_jwt_tokens(mock_user) == expected


def test_profile_cls_split_name_false(create_mock_profile):
    profile = create_mock_profile(split_name=False)

    assert profile.first_name == ""
    assert profile.last_name == ""


def test_get_client(settings, authlib_settings_github, random_vcs):
    settings.AUTHLIB_OAUTH_CLIENTS = {random_vcs: authlib_settings_github}
    client = services.get_client(vcs=random_vcs)

    assert isinstance(client, DjangoRemoteApp)


def test_get_client_raises_error(settings):
    settings.AUTHLIB_OAUTH_CLIENTS = {}
    with pytest.raises(ServiceException):
        services.get_client(vcs="error")


def test_update_token(random_vcs, fake_token, create_vcs_account):
    access_token = "12345"
    refresh_token = "67890"
    vcs_account = create_vcs_account(vcs=random_vcs, access_token=access_token, refresh_token=refresh_token)

    services.update_token(random_vcs, fake_token)
    vcs_account.refresh_from_db()
    assert vcs_account.access_token != fake_token["access_token"]
    assert vcs_account.refresh_token != fake_token["refresh_token"]
    assert vcs_account.expires_at != fake_token["expires_at"]

    services.update_token(random_vcs, fake_token, refresh_token=refresh_token)
    vcs_account.refresh_from_db()
    assert vcs_account.access_token == fake_token["access_token"]
    assert vcs_account.refresh_token == fake_token["refresh_token"]
    assert vcs_account.expires_at == fake_token["expires_at"]

    services.update_token(random_vcs, fake_token, access_token=access_token)
    vcs_account.refresh_from_db()
    assert vcs_account.access_token == fake_token["access_token"]
    assert vcs_account.refresh_token == fake_token["refresh_token"]
    assert vcs_account.expires_at == fake_token["expires_at"]
