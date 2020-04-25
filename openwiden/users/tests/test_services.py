import mock
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.test import TestCase
from openwiden.users import services, models
from openwiden.users.tests import fixtures, factories
from faker import Faker

fake = Faker()


def test_profile_cls_split_name_false():
    p = fixtures.create_random_profile(split_name=False)
    assert p.first_name is None
    assert p.last_name is None


class OAuthServiceTestCase(TestCase):
    token = {"access_token": "test_token"}
    provider = "test_provider"

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        self.oauth_token = factories.OAuth2TokenFactory(user=self.user, provider=self.provider)

    # def test_get_client(self):
    #     self.fail()
    #
    # def test_get_client_returns_none(self):
    #     self.fail()
    #
    # def test_get_token(self):
    #     self.fail()
    #
    # def get_github_profile(self):
    #     self.fail()
    #
    # def get_gitlab_profile(self):
    #     self.fail()
    #
    # def get_profile_not_implemented_error(self):
    #     self.fail()

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

    @mock.patch("openwiden.users.services.ContentFile")
    @mock.patch("openwiden.users.services.requests.get")
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

    @mock.patch("openwiden.users.services.ContentFile")
    @mock.patch("openwiden.users.services.requests.get")
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

    @mock.patch("openwiden.users.services.ContentFile")
    @mock.patch("openwiden.users.services.requests.get")
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
