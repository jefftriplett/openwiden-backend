from django.test import TestCase


from openwiden.users import serializers
from openwiden.users.models import User, OAuth2Token


class UserSerializerTestCase(TestCase):
    def test_meta(self):
        expected_fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "avatar",
        )
        self.assertEqual(serializers.UserSerializer.Meta.model, User)
        self.assertEqual(serializers.UserSerializer.Meta.fields, expected_fields)


class UserUpdateSerializerTestCase(TestCase):
    def test_meta(self):
        expected_fields = ("username", "first_name", "last_name", "avatar")
        self.assertTrue(issubclass(serializers.UserUpdateSerializer, serializers.UserSerializer))
        self.assertTrue(issubclass(serializers.UserUpdateSerializer.Meta, serializers.UserSerializer.Meta))
        self.assertEqual(serializers.UserUpdateSerializer.Meta.fields, expected_fields)


class OAuth2TokenSerializerTestCase(TestCase):
    def test_meta(self):
        expected_fields = ("provider", "login")
        self.assertEqual(serializers.OAuth2TokenSerializer.Meta.model, OAuth2Token)
        self.assertEqual(serializers.OAuth2TokenSerializer.Meta.fields, expected_fields)


class UserWithOAuthTokensSerializerTestCase(TestCase):
    def test_meta(self):
        expected_fields = serializers.UserSerializer.Meta.fields + ("oauth2_tokens",)
        self.assertTrue(issubclass(serializers.UserWithOAuthTokensSerializer, serializers.UserSerializer))
        self.assertTrue(issubclass(serializers.UserWithOAuthTokensSerializer.Meta, serializers.UserSerializer.Meta))
        self.assertEqual(serializers.UserWithOAuthTokensSerializer.Meta.fields, expected_fields)
