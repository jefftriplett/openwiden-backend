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


# import typing as t
# from unittest import mock
#
# from authlib.common.errors import AuthlibBaseError
# from authlib.integrations.django_client import DjangoRemoteApp
# from django.contrib.auth.models import AnonymousUser
# from django.core.files.base import ContentFile
# from django.test import TestCase, override_settings, SimpleTestCase
# from rest_framework_simplejwt.tokens import RefreshToken
#
# from openwiden.users import services, models
# from openwiden.services.remote import exceptions as service_exceptions, models as service_models
# from openwiden.users.tests import fixtures, factories
# from openwiden import enums
# from faker import Faker
#
# fake = Faker()
#
#
# class ProfileTest(SimpleTestCase):
#     def test_profile_cls_split_name_false(self):
#         p = fixtures.create_random_profile(split_name=False)
#         self.assertIsNone(p.first_name)
#         self.assertIsNone(p.last_name)
#
#
# class OAuthServiceTestCase(TestCase):
#     token = {"access_token": fake.pystr(), "expires_at": fake.pyint()}
#
#     def setUp(self) -> None:
#         self.provider = fake.random_element(enums.VersionControlService.values)
#         self.user = factories.UserFactory()
#         self.vcs_account = factories.VCSAccountFactory(user=self.user, provider=self.provider)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_client")
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_token")
#     def get_profile(
#         self, provider: str, p_get_token, p_get_client, profile=fixtures.create_random_profile()
#     ) -> t.Tuple[service_models.Profile, dict]:
#         mock_client = mock.MagicMock()
#         mock_client.get.side_effect = [profile, fixtures.EmailListMock()]
#         p_get_client.return_value = mock_client
#         p_get_token.return_value = self.token
#         returned_profile = services.OAuthService.get_profile(provider, mock.MagicMock())
#         return returned_profile, profile.json()
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER})
#     def test_get_client(self):
#         client: DjangoRemoteApp = services.OAuthService.get_client("github")
#         self.assertIsInstance(client, DjangoRemoteApp)
#
#     def test_get_client_raises_error(self):
#         with self.assertRaises(service_exceptions.ProviderNotFound):
#             services.OAuthService.get_client("test")
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER})
#     @mock.patch.object(DjangoRemoteApp, "authorize_access_token")
#     def test_get_token(self, p_authorize_access_token):
#         p_authorize_access_token.return_value = self.token
#         client = services.OAuthService.get_client("github")
#         mock_request = mock.MagicMock()
#         mock_request.user = AnonymousUser()
#         token = services.OAuthService.get_token(client, mock_request)
#         self.assertEqual(token, self.token)
#         self.assertEqual(p_authorize_access_token.call_count, 1)
#
#     def test_get_token_raises_fetch_exception(self):
#         mock_client = mock.MagicMock()
#         mock_client.authorize_access_token.side_effect = AuthlibBaseError(description="test")
#         with self.assertRaisesMessage(service_exceptions.TokenFetchException, "test"):
#             services.OAuthService.get_token(mock_client, mock.MagicMock())
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER})
#     def test_get_github_profile(self):
#         profile, data = self.get_profile("github")
#         expected_profile = service_models.Profile(**data, **self.token)
#         self.assertEqual(profile.to_dict(), expected_profile.to_dict())
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={"gitlab": fixtures.GITLAB_PROVIDER})
#     def test_get_gitlab_profile(self):
#         profile, data = self.get_profile("gitlab")
#         data["login"] = data.pop("username")
#         expected_profile = service_models.Profile(**data, **self.token)
#         self.assertEqual(profile.to_dict(), expected_profile.to_dict())
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={})
#     def test_get_profile_not_implemented_error(self):
#         expected_message = service_exceptions.ProviderNotImplemented("test").description
#         with self.assertRaisesMessage(service_exceptions.ProviderNotImplemented, expected_message):
#             self.get_profile("test")
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITLAB_PROVIDER})
#     @mock.patch("openwiden.users.services.oauth.repositories_tasks.remote_repositories_sync")
#     def test_get_profile_validation_error(self, p_sync):
#         profile = fixtures.create_random_profile()
#         profile.login = None
#         expected_message = service_exceptions.ProfileValidateException("errors dict from serializer").description
#         with self.assertRaisesMessage(service_exceptions.ProfileValidateException, expected_message):
#             self.get_profile("github", profile=profile)
#             self.assertEqual(p_sync.call_count, 1)
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITLAB_PROVIDER})
#     def test_get_profile_email_does_not_exist(self):
#         profile = fixtures.create_random_profile()
#         profile.email = None
#         self.get_profile("github", profile=profile)
#
#     @override_settings(AUTHLIB_OAUTH_CLIENTS={"gitlab": fixtures.GITLAB_PROVIDER})
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_client")
#     def test_get_profile_raises_profile_retrieve_exception(self, p_get_client):
#         expected_message = service_exceptions.ProfileRetrieveException("test").description
#         mock_client = mock.MagicMock()
#         mock_client.get.side_effect = AuthlibBaseError(description="test")
#         p_get_client.return_value = mock_client
#         with self.assertRaisesMessage(service_exceptions.ProfileRetrieveException, expected_message):
#             services.OAuthService.get_profile("gitlab", mock.MagicMock())
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_oauth_token_exist_authenticated_user_change_oauth_token_user(self, p_get_profile):
#         """
#         Authenticated user -> change vcs_account.user -> login is the same -> return same user
#         """
#         new_user = factories.UserFactory()
#         profile = fixtures.create_random_profile(login=self.vcs_account.login, id=self.vcs_account.remote_id)
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, new_user, mock.MagicMock())
#         self.vcs_account.refresh_from_db()
#         self.assertEqual(user.id, new_user.id)
#         self.assertEqual(self.vcs_account.login, profile.login)
#         self.assertEqual(str(self.vcs_account.user.id), user.id)
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_oauth_token_exist_authenticated_user_change_login(self, p_get_profile):
#         """
#         Authenticated user -> oauth token user is the same -> change login -> return same user
#         """
#         profile = fixtures.create_random_profile(id=self.vcs_account.remote_id)
#         old_login = self.user.username
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         self.vcs_account.refresh_from_db()
#         self.assertEqual(self.vcs_account.user.id, user.id)
#         self.assertEqual(self.vcs_account.login, profile.login)
#         self.assertNotEqual(self.vcs_account.login, old_login)
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_oauth_token_exist_authenticated_user_do_nothing(self, p_get_profile):
#         """
#         Authenticated user -> oauth token user is the same -> login is the same -> return same user
#         """
#         profile = fixtures.create_random_profile(id=self.vcs_account.remote_id, login=self.vcs_account.login)
#         old_login, old_user_id = self.vcs_account.login, self.vcs_account.user.id
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         self.vcs_account.refresh_from_db()
#         self.assertEqual(self.vcs_account.user.id, user.id)
#         self.assertEqual(self.vcs_account.login, profile.login)
#         self.assertEqual(old_login, self.vcs_account.login)
#         self.assertEqual(old_user_id, str(self.vcs_account.user.id))
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_oauth_token_exist_anonymous_user(self, p_get_profile):
#         """
#         Anonymous -> login is the same -> return vcs_account.user
#         """
#         vcs_account = factories.VCSAccountFactory(user=self.user, provider=self.provider)
#         profile = fixtures.create_random_profile(id=vcs_account.remote_id)
#         self.user = AnonymousUser()
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         vcs_account.refresh_from_db()
#         self.assertEqual(vcs_account.user.id, user.id)
#         self.assertEqual(vcs_account.login, profile.login)
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.new_token")
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     @mock.patch("openwiden.users.services.oauth.ContentFile")
#     @mock.patch("openwiden.users.services.oauth.requests.get")
#     def test_oauth_token_does_not_exist_authenticated_user(self, p_get, p_cf, p_get_profile, p_new_token):
#         """
#         Authenticated user -> create oauth token -> return authenticated user
#         """
#         profile = fixtures.create_random_profile()
#         p_get.return_value = mock.MagicMock()
#         p_cf.return_value = ContentFile(b"12345")
#         p_get_profile.return_value = profile
#         p_new_token.return_value = None
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         self.assertEqual(user.id, self.user.id)
#         self.assertEqual(p_get.call_count, 0)
#         self.assertEqual(p_cf.call_count, 0)
#         self.assertEqual(p_get_profile.call_count, 1)
#         self.assertEqual(p_new_token.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.new_token")
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     @mock.patch("openwiden.users.services.oauth.ContentFile")
#     @mock.patch("openwiden.users.services.oauth.requests.get")
#     def test_oauth_token_does_not_exist_anonymous_user(self, p_get, p_cf, p_get_profile, p_new_token):
#         """
#         Anonymous -> login does not exist -> create user -> create oauth token -> return created user
#         """
#         profile = fixtures.create_random_profile()
#         p_get.return_value = mock.MagicMock()
#         p_cf.return_value = ContentFile(b"12345")
#         p_get_profile.return_value = profile
#         p_new_token.return_value = None
#         self.user = AnonymousUser()
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         user_from_db = models.User.objects.get(username=profile.login)
#         self.assertEqual(user.id, user_from_db.id)
#         self.assertEqual(p_get.call_count, 1)
#         self.assertEqual(p_cf.call_count, 1)
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.new_token")
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     @mock.patch("openwiden.users.services.oauth.ContentFile")
#     @mock.patch("openwiden.users.services.oauth.requests.get")
#     def test_oauth_token_does_not_exist_anonymous_user_login_exist(self, p_get, p_cf, p_get_profile, new_token):
#         """
#         Anonymous -> login exist -> generate new login -> create user -> create oauth token -> return created user
#         """
#         profile = fixtures.create_random_profile(login=self.user.username)
#         expected_username = profile.login + "_"
#         p_get.return_value = mock.MagicMock()
#         p_cf.return_value = ContentFile(b"12345")
#         p_get_profile.return_value = profile
#         new_token.return_value = None
#         self.user = AnonymousUser()
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         user_from_db = models.User.objects.get(username=profile.login)
#         self.assertEqual(user.id, user_from_db.id)
#         self.assertTrue(str(user.username).startswith(expected_username))
#         self.assertEqual(p_get.call_count, 1)
#         self.assertEqual(p_cf.call_count, 1)
#         self.assertEqual(p_get_profile.call_count, 1)
#
#
# class UserServiceTestCase(TestCase):
#     @mock.patch("openwiden.users.services.user.RefreshToken.for_user")
#     def test_get_jwt(self, p_refresh):
#         user = factories.UserFactory()
#         token = RefreshToken.for_user(user)
#         self.assertEqual(p_refresh.call_count, 1)
#         p_refresh.return_value = token
#         jwt_tokens = services.UserService.get_jwt(user)
#         expected_dict = dict(access=str(token.access_token), refresh=str(token))
#         self.assertEqual(jwt_tokens, expected_dict)
#         self.assertEqual(p_refresh.call_count, 2)
