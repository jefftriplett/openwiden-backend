import mock
import typing as t
from authlib.common.errors import AuthlibBaseError
from authlib.integrations.django_client import DjangoRemoteApp
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from rest_framework_simplejwt.tokens import RefreshToken

from openwiden.users import services, models
from openwiden.users.services import exceptions as service_exceptions, models as service_models
from openwiden.users.tests import fixtures, factories
from faker import Faker

fake = Faker()


def test_profile_cls_split_name_false():
    p = fixtures.create_random_profile(split_name=False)
    assert p.first_name is None
    assert p.last_name is None


class OAuthServiceTestCase(TestCase):
    token = {"access_token": fake.pystr(), "expires_at": fake.pyint()}
    provider = "test_provider"

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        self.oauth_token = factories.OAuth2TokenFactory(user=self.user, provider=self.provider)

    @mock.patch("openwiden.users.services.oauth.OAuthService.get_client")
    @mock.patch("openwiden.users.services.oauth.OAuthService.get_token")
    def get_profile(
        self, provider: str, p_get_token, p_get_client, profile=fixtures.create_random_profile()
    ) -> t.Tuple[service_models.Profile, dict]:
        mock_client = mock.MagicMock()
        mock_client.get.return_value = profile
        p_get_client.return_value = mock_client
        p_get_token.return_value = self.token
        returned_profile = services.OAuthService.get_profile(provider, mock.MagicMock())
        return returned_profile, profile.json()

    @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER})
    def test_get_client(self):
        client: DjangoRemoteApp = services.OAuthService.get_client("github")
        self.assertIsInstance(client, DjangoRemoteApp)

    def test_get_client_raises_error(self):
        with self.assertRaises(service_exceptions.ProviderNotFound):
            services.OAuthService.get_client("test")

    @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER})
    @mock.patch.object(DjangoRemoteApp, "authorize_access_token")
    def test_get_token(self, p_authorize_access_token):
        p_authorize_access_token.return_value = self.token
        client = services.OAuthService.get_client("github")
        mock_request = mock.MagicMock()
        mock_request.user = AnonymousUser()
        token = services.OAuthService.get_token(client, mock_request)
        self.assertEqual(token, self.token)
        self.assertEqual(p_authorize_access_token.call_count, 1)

    def test_get_token_raises_fetch_exception(self):
        mock_client = mock.MagicMock()
        mock_client.authorize_access_token.side_effect = AuthlibBaseError(description="test")
        with self.assertRaisesMessage(service_exceptions.TokenFetchException, "test"):
            services.OAuthService.get_token(mock_client, mock.MagicMock())

    @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER})
    def test_get_github_profile(self):
        profile, data = self.get_profile("github")
        expected_profile = service_models.Profile(**data, **self.token)
        self.assertEqual(profile.to_dict(), expected_profile.to_dict())

    @override_settings(AUTHLIB_OAUTH_CLIENTS={"gitlab": fixtures.GITLAB_PROVIDER})
    def test_get_gitlab_profile(self):
        profile, data = self.get_profile("gitlab")
        data["login"] = data.pop("username")
        expected_profile = service_models.Profile(**data, **self.token)
        self.assertEqual(profile.to_dict(), expected_profile.to_dict())

    @override_settings(AUTHLIB_OAUTH_CLIENTS={})
    def test_get_profile_not_implemented_error(self):
        expected_message = service_exceptions.ProviderNotImplemented("test").description
        with self.assertRaisesMessage(service_exceptions.ProviderNotImplemented, expected_message):
            self.get_profile("test")

    def test_oauth_token_exist_authenticated_user_change_oauth_token_user(self):
        """
        Authenticated user -> change oauth_token.user -> login is the same -> return same user
        """
        new_user = factories.UserFactory()
        profile = fixtures.create_random_profile(login=self.oauth_token.login, id=self.oauth_token.remote_id)
        user = services.OAuthService.oauth(self.provider, new_user, profile)
        self.oauth_token.refresh_from_db()
        self.assertEqual(user.id, new_user.id)
        self.assertEqual(self.oauth_token.login, profile.login)
        self.assertEqual(str(self.oauth_token.user.id), user.id)

    def test_oauth_token_exist_authenticated_user_change_login(self):
        """
        Authenticated user -> oauth token user is the same -> change login -> return same user
        """
        profile = fixtures.create_random_profile(id=self.oauth_token.remote_id)
        old_login = self.user.username
        user = services.OAuthService.oauth(self.provider, self.user, profile)
        self.oauth_token.refresh_from_db()
        self.assertEqual(self.oauth_token.user.id, user.id)
        self.assertEqual(self.oauth_token.login, profile.login)
        self.assertNotEqual(self.oauth_token.login, old_login)

    def test_oauth_token_exist_authenticated_user_do_nothing(self):
        """
        Authenticated user -> oauth token user is the same -> login is the same -> return same user
        """
        profile = fixtures.create_random_profile(id=self.oauth_token.remote_id, login=self.oauth_token.login)
        old_login, old_user_id = self.oauth_token.login, self.oauth_token.user.id
        user = services.OAuthService.oauth(self.provider, self.user, profile)
        self.oauth_token.refresh_from_db()
        self.assertEqual(self.oauth_token.user.id, user.id)
        self.assertEqual(self.oauth_token.login, profile.login)
        self.assertEqual(old_login, self.oauth_token.login)
        self.assertEqual(old_user_id, str(self.oauth_token.user.id))

    def test_oauth_token_exist_anonymous_user(self):
        """
        Anonymous -> login is the same -> return oauth_token.user
        """
        oauth_token = factories.OAuth2TokenFactory(user=self.user, provider=self.provider)
        profile = fixtures.create_random_profile(id=oauth_token.remote_id)
        self.user = AnonymousUser()
        user = services.OAuthService.oauth(self.provider, self.user, profile)
        oauth_token.refresh_from_db()
        self.assertEqual(oauth_token.user.id, user.id)
        self.assertEqual(oauth_token.login, profile.login)

    @mock.patch("openwiden.users.services.oauth.ContentFile")
    @mock.patch("openwiden.users.services.oauth.requests.get")
    def test_oauth_token_does_not_exist_authenticated_user(self, p_get, p_cf):
        """
        Authenticated user -> create oauth token -> return authenticated user
        """
        profile = fixtures.create_random_profile()
        p_get.return_value = mock.MagicMock()
        p_cf.return_value = ContentFile(b"12345")
        user = services.OAuthService.oauth(self.provider, self.user, profile)
        created_oauth_token = models.OAuth2Token.objects.get(user=user, provider=self.provider, remote_id=profile.id)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(p_get.call_count, 0)
        self.assertEqual(p_cf.call_count, 0)
        self.assertEqual(created_oauth_token.remote_id, profile.id)
        self.assertEqual(created_oauth_token.login, profile.login)

    @mock.patch("openwiden.users.services.oauth.ContentFile")
    @mock.patch("openwiden.users.services.oauth.requests.get")
    def test_oauth_token_does_not_exist_anonymous_user(self, p_get, p_cf):
        """
        Anonymous -> login does not exist -> create user -> create oauth token -> return created user
        """
        profile = fixtures.create_random_profile()
        p_get.return_value = mock.MagicMock()
        p_cf.return_value = ContentFile(b"12345")
        self.user = AnonymousUser()
        user = services.OAuthService.oauth(self.provider, self.user, profile)
        user_from_db = models.User.objects.get(username=profile.login)
        created_oauth_token = user_from_db.oauth2_tokens.first()
        self.assertEqual(user.id, user_from_db.id)
        self.assertEqual(user_from_db.oauth2_tokens.count(), 1)
        self.assertEqual(p_get.call_count, 1)
        self.assertEqual(p_cf.call_count, 1)
        self.assertEqual(created_oauth_token.provider, self.provider)
        self.assertEqual(created_oauth_token.remote_id, profile.id)

    @mock.patch("openwiden.users.services.oauth.ContentFile")
    @mock.patch("openwiden.users.services.oauth.requests.get")
    def test_oauth_token_does_not_exist_anonymous_user_login_exist(self, p_get, p_cf):
        """
        Anonymous -> login exist -> generate new login -> create user -> create oauth token -> return created user
        """
        profile = fixtures.create_random_profile(login=self.user.username)
        expected_username = profile.login + "_"
        p_get.return_value = mock.MagicMock()
        p_cf.return_value = ContentFile(b"12345")
        self.user = AnonymousUser()
        user = services.OAuthService.oauth(self.provider, self.user, profile)
        user_from_db = models.User.objects.get(username=profile.login)
        self.assertEqual(user.id, user_from_db.id)
        self.assertTrue(str(user.username).startswith(expected_username))
        self.assertEqual(p_get.call_count, 1)
        self.assertEqual(p_cf.call_count, 1)


class UserServiceTestCase(TestCase):
    @mock.patch("openwiden.users.services.user.RefreshToken.for_user")
    def test_get_jwt(self, p_refresh):
        user = factories.UserFactory()
        token = RefreshToken.for_user(user)
        self.assertEqual(p_refresh.call_count, 1)
        p_refresh.return_value = token
        jwt_tokens = services.UserService.get_jwt(user)
        expected_dict = dict(access=str(token.access_token), refresh=str(token))
        self.assertEqual(jwt_tokens, expected_dict)
        self.assertEqual(p_refresh.call_count, 2)
