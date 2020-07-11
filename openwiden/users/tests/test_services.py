from typing import Tuple
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


@pytest.mark.parametrize(
    "split_name, name, expected",
    [
        pytest.param(True, "No Name", ("No", "Name"), id="split with name"),
        pytest.param(False, "No Name", ("", ""), id="no split"),
        pytest.param(True, None, ("", ""), id="split when name is None"),
    ],
)
def test_profile_split_name_false(
    create_mock_profile, split_name: bool, name: str, expected: Tuple[str],
):
    profile = create_mock_profile(split_name=split_name, name=name)

    assert profile.first_name == expected[0]
    assert profile.last_name == expected[1]


def test_get_client_exist(settings, authlib_settings_github, random_vcs):
    settings.AUTHLIB_OAUTH_CLIENTS = {random_vcs: authlib_settings_github}
    client = services.get_client(vcs=random_vcs)

    assert isinstance(client, DjangoRemoteApp)


def test_get_client_raises_error(settings):
    settings.AUTHLIB_OAUTH_CLIENTS = {}
    with pytest.raises(ServiceException):
        services.get_client(vcs="error")


@pytest.mark.parametrize(
    "refresh_token, access_token",
    [
        pytest.param(None, None, id="nothing to update"),
        pytest.param("access_token", None, id="access token"),
        pytest.param(None, "refresh_token", id="refresh token"),
        pytest.param("access_token", "refresh_token", id="access & refresh tokens"),
    ],
)
def test_update_token(random_vcs, fake_token: dict, create_vcs_account, refresh_token: str, access_token: str):
    factory_init_kwargs = {}
    if refresh_token:
        factory_init_kwargs["refresh_token"] = refresh_token
    if access_token:
        factory_init_kwargs["access_token"] = access_token

    vcs_account = create_vcs_account(vcs=random_vcs, **factory_init_kwargs)
    services.update_token(vcs=random_vcs, token=fake_token, refresh_token=refresh_token, access_token=access_token)
    vcs_account.refresh_from_db()

    if refresh_token or access_token:
        assert vcs_account.refresh_token == fake_token["refresh_token"]
        assert vcs_account.access_token == fake_token["access_token"]
        assert vcs_account.expires_at == fake_token["expires_at"]
    else:
        assert vcs_account.access_token != fake_token["access_token"]
        assert vcs_account.refresh_token != fake_token["refresh_token"]
        assert vcs_account.expires_at != fake_token["expires_at"]
