from django.test import TestCase


from users.serializers import UserSerializer, UserUpdateSerializer, OAuth2TokenSerializer, UserWithOAuthTokensSerializer
from users.models import User, OAuth2Token


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
        self.assertEqual(UserSerializer.Meta.model, User)
        self.assertEqual(UserSerializer.Meta.fields, expected_fields)


class UserUpdateSerializerTestCase(TestCase):
    def test_meta(self):
        expected_fields = ("username", "first_name", "last_name", "avatar")
        self.assertTrue(issubclass(UserUpdateSerializer, UserSerializer))
        self.assertTrue(issubclass(UserUpdateSerializer.Meta, UserSerializer.Meta))
        self.assertEqual(UserUpdateSerializer.Meta.fields, expected_fields)


class OAuth2TokenSerializerTestCase(TestCase):
    def test_meta(self):
        expected_fields = ("provider", "login")
        self.assertEqual(OAuth2TokenSerializer.Meta.model, OAuth2Token)
        self.assertEqual(OAuth2TokenSerializer.Meta.fields, expected_fields)


class UserWithOAuthTokensSerializerTestCase(TestCase):
    def test_meta(self):
        expected_fields = UserSerializer.Meta.fields + ("oauth2_tokens",)
        self.assertTrue(issubclass(UserWithOAuthTokensSerializer, UserSerializer))
        self.assertTrue(issubclass(UserWithOAuthTokensSerializer.Meta, UserSerializer.Meta))
        self.assertEqual(UserWithOAuthTokensSerializer.Meta.fields, expected_fields)
