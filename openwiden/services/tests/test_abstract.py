import pytest
from authlib.common.errors import AuthlibBaseError

from authlib.integrations.django_client import DjangoRemoteApp

from openwiden.services import get_service
from openwiden.services.abstract import RemoteService, update_token
from openwiden.exceptions import ServiceException
from openwiden.enums import VersionControlService

pytestmark = pytest.mark.django_db


def test_profile_cls_split_name_false(create_profile):
    profile = create_profile(split_name=False)

    assert profile.first_name is None
    assert profile.last_name is None


def test_get_client(settings, authlib_settings_github, random_vcs):
    settings.AUTHLIB_OAUTH_CLIENTS = {random_vcs: authlib_settings_github}
    client = get_service(vcs=random_vcs).get_client()

    assert isinstance(client, DjangoRemoteApp)


def test_get_client_raises_error(monkeypatch):
    monkeypatch.setattr(RemoteService, "__abstractmethods__", set)

    with pytest.raises(ServiceException):
        service = get_service(vcs=VersionControlService.GITHUB.value)
        service.vcs = "error"
        service.get_client()


def test_get_token(settings, authlib_settings_github, monkeypatch, fake_token, api_rf, anonymous_user, random_vcs):
    def return_fake_token(*args):
        return fake_token

    monkeypatch.setattr(DjangoRemoteApp, "authorize_access_token", return_fake_token)
    settings.AUTHLIB_OAUTH_CLIENTS = {random_vcs: authlib_settings_github}
    mock_request = api_rf.get("/fake-url/")
    mock_request.user = anonymous_user
    token = get_service(vcs=random_vcs).get_token(mock_request)

    assert token == fake_token


def test_get_token_raises_service_exception(settings, authlib_settings_github, monkeypatch, api_rf, random_vcs):
    settings.AUTHLIB_OAUTH_CLIENTS = {random_vcs: authlib_settings_github}

    class MockAuthlibClient:
        def authorize_access_token(self, *args):
            raise AuthlibBaseError(description="test")

    request = api_rf.get("/fake-url/")
    client = MockAuthlibClient()

    with pytest.raises(ServiceException) as e:
        service = get_service(vcs=random_vcs)
        service.client = client
        service.get_token(request)

    assert e.value.args[0] == "test"


def test_update_token(random_vcs, fake_token, create_vcs_account):
    access_token = "12345"
    refresh_token = "67890"
    vcs_account = create_vcs_account(vcs=random_vcs, access_token=access_token, refresh_token=refresh_token)

    update_token(random_vcs, fake_token)
    vcs_account.refresh_from_db()
    assert vcs_account.access_token != fake_token["access_token"]
    assert vcs_account.refresh_token != fake_token["refresh_token"]
    assert vcs_account.expires_at != fake_token["expires_at"]

    update_token(random_vcs, fake_token, refresh_token=refresh_token)
    vcs_account.refresh_from_db()
    assert vcs_account.access_token == fake_token["access_token"]
    assert vcs_account.refresh_token == fake_token["refresh_token"]
    assert vcs_account.expires_at == fake_token["expires_at"]

    update_token(random_vcs, fake_token, access_token=access_token)
    vcs_account.refresh_from_db()
    assert vcs_account.access_token == fake_token["access_token"]
    assert vcs_account.refresh_token == fake_token["refresh_token"]
    assert vcs_account.expires_at == fake_token["expires_at"]


# @mock.patch("openwiden.users.services.oauth.OAuthService.get_client")
# @mock.patch("openwiden.users.services.oauth.OAuthService.get_token")
# def get_profile(
#     self, provider: str, p_get_token, p_get_client, profile=fixtures.create_random_profile()
# ) -> t.Tuple[service_models.Profile, dict]:
#     mock_client = mock.MagicMock()
#     mock_client.get.side_effect = [profile, fixtures.EmailListMock()]
#     p_get_client.return_value = mock_client
#     p_get_token.return_value = self.token
#     returned_profile = services.OAuthService.get_profile(provider, mock.MagicMock())
#     return returned_profile, profile.json()


# def test_get_github_profile(settings, authlib_settings_github, monkeypatch):
#     settings.AUTHLIB_OAUTH_CLIENTS = {"github": authlib_settings_github}
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_client")
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_token")
#
# profile, data = self.get_profile("github")
# expected_profile = service_models.Profile(**data, **self.token)
#
# self.assertEqual(profile.to_dict(), expected_profile.to_dict())

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
#         Authenticated user -> change oauth_token.user -> login is the same -> return same user
#         """
#         new_user = factories.UserFactory()
#         profile = fixtures.create_random_profile(login=self.oauth_token.login, id=self.oauth_token.remote_id)
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, new_user, mock.MagicMock())
#         self.oauth_token.refresh_from_db()
#         self.assertEqual(user.id, new_user.id)
#         self.assertEqual(self.oauth_token.login, profile.login)
#         self.assertEqual(str(self.oauth_token.user.id), user.id)
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_oauth_token_exist_authenticated_user_change_login(self, p_get_profile):
#         """
#         Authenticated user -> oauth token user is the same -> change login -> return same user
#         """
#         profile = fixtures.create_random_profile(id=self.oauth_token.remote_id)
#         old_login = self.user.username
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         self.oauth_token.refresh_from_db()
#         self.assertEqual(self.oauth_token.user.id, user.id)
#         self.assertEqual(self.oauth_token.login, profile.login)
#         self.assertNotEqual(self.oauth_token.login, old_login)
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_oauth_token_exist_authenticated_user_do_nothing(self, p_get_profile):
#         """
#         Authenticated user -> oauth token user is the same -> login is the same -> return same user
#         """
#         profile = fixtures.create_random_profile(id=self.oauth_token.remote_id, login=self.oauth_token.login)
#         old_login, old_user_id = self.oauth_token.login, self.oauth_token.user.id
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         self.oauth_token.refresh_from_db()
#         self.assertEqual(self.oauth_token.user.id, user.id)
#         self.assertEqual(self.oauth_token.login, profile.login)
#         self.assertEqual(old_login, self.oauth_token.login)
#         self.assertEqual(old_user_id, str(self.oauth_token.user.id))
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_oauth_token_exist_anonymous_user(self, p_get_profile):
#         """
#         Anonymous -> login is the same -> return oauth_token.user
#         """
#         oauth_token = factories.OAuth2TokenFactory(user=self.user, provider=self.provider)
#         profile = fixtures.create_random_profile(id=oauth_token.remote_id)
#         self.user = AnonymousUser()
#         p_get_profile.return_value = profile
#         user = services.OAuthService.oauth(self.provider, self.user, mock.MagicMock())
#         oauth_token.refresh_from_db()
#         self.assertEqual(oauth_token.user.id, user.id)
#         self.assertEqual(oauth_token.login, profile.login)
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
