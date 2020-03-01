from django.test import TestCase
from django.forms.models import model_to_dict
from faker import Faker
from nose.tools import eq_, ok_
from .factories import UserFactory
from openwiden.users.serializers import GitHubOAuthCodeSerializer, CreateUserSerializer


fake = Faker()


class TestCreateUserSerializer(TestCase):
    """
    Tests CreateUserSerializer for user creation.
    """

    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = CreateUserSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())


class TestGitHubOAuthCodeSerializer(TestCase):
    """
    Tests GitHubOAuthCodeSerializer for code validation.
    """

    def setUp(self) -> None:
        self.user_data = model_to_dict(UserFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = GitHubOAuthCodeSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        data = {"code": fake.pystr(min_chars=20, max_chars=20)}
        serializer = GitHubOAuthCodeSerializer(data=data)
        eq_(serializer.is_valid(), True, msg=serializer.errors)
