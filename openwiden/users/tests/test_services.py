import pytest

from openwiden.users import services


class TestUserService:
    def test_get_jwt(self, monkeypatch, mock_user, create_mock_refresh_token):
        expected = dict(access="12345", refresh="67890")

        def get_mock_refresh_token(*args):
            return create_mock_refresh_token(**expected)

        monkeypatch.setattr(services.RefreshToken, "for_user", get_mock_refresh_token)

        assert services.UserService.get_jwt(mock_user) == expected


class TestVCSAccountService:
    def test_find(self, monkeypatch, mock_vcs_account, mock_user):
        def return_mock_vcs_account(**kwargs):
            return mock_vcs_account

        monkeypatch.setattr(services.models.VCSAccount.objects, "get", return_mock_vcs_account)

        oauth_token = services.VCSAccount.find(mock_user, "test")

        assert oauth_token == mock_vcs_account

    def test_find_raises_service_exception(self, monkeypatch, mock_user):
        def raise_does_not_exist(**kwargs):
            raise services.models.VCSAccount.DoesNotExist

        monkeypatch.setattr(services.models.VCSAccount.objects, "get", raise_does_not_exist)

        with pytest.raises(services.exceptions.ServiceException) as e:
            services.VCSAccount.find(mock_user, "test")

            assert e.value == services.error_messages.VCS_ACCOUNT_DOES_NOT_EXIST.format(vcs="test")
