from django.test import TestCase
from django.forms.models import model_to_dict
from nose.tools import eq_, ok_
from .factories import UserFactory
from openwiden.users.serializers import CreateUserSerializer


class TestCreateUserSerializer(TestCase):
    def setUp(self):
        self.user_data = model_to_dict(UserFactory.build())

    def test_serializer_with_empty_data(self):
        serializer = CreateUserSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = CreateUserSerializer(data={"code": "test_code"})
        ok_(serializer.is_valid())

    def test_serializer_retrieves_github_token_on_save(self):
        serializer = CreateUserSerializer(data=self.user_data)
        ok_(serializer.is_valid())

        user = serializer.save()
        ok_(user.github_token)
