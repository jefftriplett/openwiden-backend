import mock
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.test import TestCase
from openwiden.users import utils
from faker import Faker
from .. import models
from .factories import OAuth2TokenFactory, UserFactory

fake = Faker()


def create_random_profile(
    id=fake.pyint(), login=fake.pystr(), name=fake.name(), email=fake.email(), avatar_url=fake.url(), split_name=True,
) -> utils.Profile:
    return utils.Profile(id=id, login=login, name=name, email=email, avatar_url=avatar_url, split_name=split_name)


def test_profile_cls_split_name_false():
    p = create_random_profile(split_name=False)
    assert p.first_name is None
    assert p.last_name is None


class CreateOrUpdateUserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.token = {"access_token": "test_token"}
        cls.provider = "test_provider"
        cls.fake_profile = create_random_profile()

        cls.mock_client = mock.MagicMock()
        cls.mock_client.authorize_access_token.return_value = cls.token
        cls.mock_request = mock.MagicMock()
        cls.mock_request.user = AnonymousUser()

    def create_or_update_user(self):
        return utils.create_or_update_user(self.provider, self.mock_client, self.mock_request)


@mock.patch("openwiden.users.utils.get_profile")
class CreateOrUpdateUserTokenExistsTestCase(CreateOrUpdateUserTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.oauth2_token = OAuth2TokenFactory.create(provider=cls.provider, remote_id=cls.fake_profile.id)

    def test_anonymous_user(self, patched_get_profile):
        """
        Test that returns exists user from oauth token.
        """
        login = "new_login"
        self.fake_profile.login = login
        self.oauth2_token.login = "to_change"
        self.oauth2_token.save()
        patched_get_profile.return_value = self.fake_profile

        user = self.create_or_update_user()

        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        self.assertEqual(models.OAuth2Token.objects.get(id=self.oauth2_token.id).login, login)
        self.assertEqual(str(user.id), str(self.oauth2_token.user.id))

    def test_auth_user_equals_oauth_token_user(self, patched_get_profile):
        """
        Test that nothing happens (request user equals oauth token user).
        """
        login = "the_same"
        factory_user = UserFactory.create(username="the_same")
        self.fake_profile.login = login
        self.oauth2_token.login = login
        self.mock_request.user = factory_user
        self.oauth2_token.user = factory_user
        self.oauth2_token.save()
        patched_get_profile.return_value = self.fake_profile

        user = self.create_or_update_user()
        oauth2_token = models.OAuth2Token.objects.get(id=self.oauth2_token.id)

        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        ids = {str(factory_user.id), str(user.id), str(oauth2_token.user.id)}
        self.assertEqual(len(ids), 1)

    def test_auth_user_not_equals_oauth_token_user(self, patched_get_profile):
        """
        Test that oauth token user changed to request user and saved.
        """
        old_user, new_user = UserFactory.create_batch(2)
        self.mock_request.user = new_user
        self.oauth2_token.user = old_user
        self.oauth2_token.save()
        patched_get_profile.return_value = self.fake_profile

        user = self.create_or_update_user()
        oauth2_token = models.OAuth2Token.objects.get(id=self.oauth2_token.id)

        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        self.assertNotEqual(str(old_user.id), str(new_user.id))
        self.assertEqual(str(new_user.id), str(user.id))
        self.assertEqual(str(oauth2_token.user.id), str(new_user.id))


@mock.patch("openwiden.users.utils.get_profile")
class CreateOrUpdateUserTokenDoesNotExistsTestCase(CreateOrUpdateUserTestCase):
    @mock.patch("openwiden.users.utils.ContentFile")
    @mock.patch("openwiden.users.utils.requests.get")
    def test_anonymous_user(self, patched_requests_get, patched_content_file, patched_get_profile):
        """
        Test that creates new User & OAuth2Token for that user.
        """
        patched_get_profile.return_value = self.fake_profile
        patched_requests_get.return_value = mock.MagicMock()
        patched_content_file.return_value = ContentFile(b"12345")
        user = self.create_or_update_user()
        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(str(user.id), str(models.User.objects.first().id))
        self.assertEqual(models.OAuth2Token.objects.count(), 1)

    @mock.patch("openwiden.users.utils.ContentFile")
    @mock.patch("openwiden.users.utils.requests.get")
    def test_anonymous_user_login_exists(self, patched_requests_get, patched_content_file, patched_get_profile):
        UserFactory.create(username=self.fake_profile.login)
        patched_get_profile.return_value = self.fake_profile
        patched_requests_get.return_value = mock.MagicMock()
        patched_content_file.return_value = ContentFile(b"12345")
        user = self.create_or_update_user()
        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        qs = models.OAuth2Token.objects.filter(user=user)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().login, self.fake_profile.login)

    def test_auth_user_create_new_oauth_token(self, patched_get_profile):
        factory_token = OAuth2TokenFactory.create()
        patched_get_profile.return_value = self.fake_profile
        self.mock_request.user = factory_token.user
        user = self.create_or_update_user()
        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        qs = models.OAuth2Token.objects.filter(user=user)
        self.assertEqual(qs.count(), 2)


class GetProfile(TestCase):
    @staticmethod
    def get_random_profile_data():
        return {
            "id": fake.pyint(),
            "login": fake.user_name(),
            "name": fake.name(),
            "email": fake.email(),
            "avatar_url": fake.url(),
        }

    def test_github(self):
        mock_client = mock.MagicMock()
        mock_profile = mock.MagicMock()
        mock_profile.json.return_value = self.get_random_profile_data()
        mock_client.get.return_value = mock_profile
        utils.get_profile("github", mock_client, "token")

    def test_gitlab(self):
        mock_client = mock.MagicMock()
        mock_profile = mock.MagicMock()
        fake_profile_data = self.get_random_profile_data()
        username = fake_profile_data.pop("login")
        fake_profile_data["username"] = username
        mock_profile.json.return_value = fake_profile_data
        mock_client.get.return_value = mock_profile
        profile = utils.get_profile("gitlab", mock_client, "token")
        self.assertEqual(profile.login, username)

    def test_none(self):
        mock_client = mock.MagicMock()
        utils.get_profile("none", mock_client, "token")
