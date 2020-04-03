import mock
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.test import TestCase
from users import utils
from faker import Faker
from users import models
from .factories import OAuth2TokenFactory, UserFactory

fake = Faker()


def create_random_profile(
    id=str(fake.pyint()),
    login=fake.pystr(),
    name=fake.name(),
    email=fake.email(),
    avatar_url=fake.url(),
    split_name=True,
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


@mock.patch("users.utils.get_profile")
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

        user = utils.create_or_update_user(self.provider, self.mock_client, self.mock_request)

        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        self.assertEqual(models.OAuth2Token.objects.get(id=self.oauth2_token.id).login, login)
        self.assertEqual(str(user.id), str(self.oauth2_token.user.id))

    def test_auth_user_equals_oauth_token_user(self, patched_get_profile):
        """
        Test that nothing happens (request user equals oauth token user).
        """
        factory_user = UserFactory.create()
        self.mock_request.user = factory_user
        self.oauth2_token.user = factory_user
        self.oauth2_token.save()
        patched_get_profile.return_value = self.fake_profile

        user = utils.create_or_update_user(self.provider, self.mock_client, self.mock_request)
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

        user = utils.create_or_update_user(self.provider, self.mock_client, self.mock_request)
        oauth2_token = models.OAuth2Token.objects.get(id=self.oauth2_token.id)

        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        self.assertNotEqual(str(old_user.id), str(new_user.id))
        self.assertEqual(str(new_user.id), str(user.id))
        self.assertEqual(str(oauth2_token.user.id), str(new_user.id))


@mock.patch("users.utils.get_profile")
class CreateOrUpdateUserTokenDoesNotExistsTestCase(CreateOrUpdateUserTestCase):
    @mock.patch("users.utils.ContentFile")
    @mock.patch("users.utils.requests.get")
    def test_anonymous_user(
        self, patched_requests_get, patched_content_file, patched_get_profile,
    ):
        """
        Test that creates new User & OAuth2Token for that user.
        """
        patched_get_profile.return_value = self.fake_profile
        patched_requests_get.return_value = mock.MagicMock()
        patched_content_file.return_value = ContentFile(b"12345")
        user = utils.create_or_update_user(self.provider, self.mock_client, self.mock_request)
        patched_get_profile.assert_called_once_with(self.provider, self.mock_client, self.token)
        self.assertEqual(models.User.objects.count(), 1)
        self.assertEqual(str(user.id), str(models.User.objects.first().id))
        self.assertEqual(models.OAuth2Token.objects.count(), 1)
