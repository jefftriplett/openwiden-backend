from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel

from openwiden.tests.cases import ModelTestCase
from openwiden.users.tests import factories


class UserModelTestCase(ModelTestCase):
    """
    User model test case.
    """

    factory = factories.UserFactory

    def test_model_meta(self):
        self.assertEqual(str(self.meta.verbose_name), _("user"))
        self.assertEqual(str(self.meta.verbose_name_plural), _("users"))

    def test_user_inherits_from_abs_user_and_uuid_model(self):
        self.assertTrue(issubclass(self.model, AbstractUser))
        self.assertTrue(issubclass(self.model, UUIDModel))


class OAuth2TokenModelTestCase(ModelTestCase):
    """
    OAuth2Token model test case.
    """

    factory = factories.OAuth2TokenFactory

    def test_model_meta(self):
        self.assertEqual(str(self.meta.verbose_name), _("oauth2 token"))
        self.assertEqual(str(self.meta.verbose_name_plural), _("oauth2 tokens"))

    def test_provider_field(self):
        self.assertFieldMaxLength("provider", 40)
        self.assertFieldVerboseNameEqual("provider", _("provider name"))

    def test_remote_id_field(self):
        self.assertFieldVerboseNameEqual("remote_id", _("user id from provider site"))

    def test_login_field(self):
        self.assertFieldMaxLength("login", 150)
        self.assertFieldVerboseNameEqual("login", _("login"))

    def test_token_type_field(self):
        self.assertFieldMaxLength("token_type", 40)
        self.assertFieldVerboseNameEqual("token_type", _("token type"))

    def test_access_token_field(self):
        self.assertFieldMaxLength("access_token", 200)
        self.assertFieldVerboseNameEqual("access_token", _("access token"))

    def test_refresh_token_field(self):
        self.assertFieldMaxLength("refresh_token", 200)
        self.assertFieldVerboseNameEqual("refresh_token", _("refresh token"))

    def test_expires_at_field(self):
        self.assertFieldVerboseNameEqual("expires_at", _("expiration date in seconds"))

    def test_str_returns_access_token(self):
        self.assertEqual(str(self.instance), self.instance.access_token)

    def test_to_dict_method(self):
        expected_dict = {
            "access_token": self.instance.access_token,
            "token_type": self.instance.token_type,
            "refresh_token": self.instance.refresh_token,
            "expires_at": self.instance.expires_at,
        }
        self.assertEqual(self.instance.to_token(), expected_dict)
