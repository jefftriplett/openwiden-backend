from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from openwiden.users.test.factories import UserFactory


class UserModelTestCase(TestCase):
    """
    User model test case.
    """

    def setUp(self) -> None:
        self.user = UserFactory()
        self.model = UserFactory._meta.model
        self.meta = self.model._meta

    def get_field_attr(self, field, attr):
        """
        Returns model field attr by key.
        """
        field = self.meta.get_field(field)
        return getattr(field, attr)

    def assertFieldVerboseNameEqual(self, field: str, label: str = None):
        """
        Asserts that field verbose name equals for specified label.
        """
        verbose_name = self.get_field_attr(field, "verbose_name")
        self.assertEqual(verbose_name, label or _(field))

    def assertFieldMaxLength(self, field, length):
        """
        Asserts that field max length equals for specified length.
        """
        max_length = self.get_field_attr(field, "max_length")
        self.assertEqual(max_length, length)

    def test_model_str_returns_username(self):
        self.assertEqual(str(self.user), self.user.login)

    def test_model_meta(self):
        self.assertEqual(str(self.meta.verbose_name), _("user"))
        self.assertEqual(str(self.meta.verbose_name_plural), _("users"))

    def test_username_field_constant(self):
        self.assertEqual(self.model.USERNAME_FIELD, "login")

    def test_required_fields(self):
        self.assertEqual(self.model.REQUIRED_FIELDS, [])

    def test_id_field_verbose_name(self):
        self.assertFieldVerboseNameEqual("id")

    def test_login_field_verbose_name(self):
        self.assertFieldVerboseNameEqual("login")

    def test_name_field_verbose_name(self):
        self.assertFieldVerboseNameEqual("name")

    def test_email_field_verbose_name(self):
        self.assertFieldVerboseNameEqual("email", _("e-mail"))

    def test_github_token_verbose_name(self):
        self.assertFieldVerboseNameEqual("github_token", _("GitHub token"))

    def test_logic_field_max_length(self):
        self.assertFieldMaxLength("login", 255)

    def test_name_field_max_length(self):
        self.assertFieldMaxLength("name", 255)
