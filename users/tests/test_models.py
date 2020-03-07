from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel

from openwiden.tests.cases import ModelTestCase
from .factories import UserFactory
from faker import Faker


fake = Faker()


class UserModelTestCase(ModelTestCase):
    """
    User model test case.
    """

    factory = UserFactory

    def test_model_meta(self):
        self.assertEqual(str(self.meta.verbose_name), _("user"))
        self.assertEqual(str(self.meta.verbose_name_plural), _("users"))

    def test_user_inherits_from_abs_user_and_uuid_model(self):
        self.assertTrue(issubclass(self.model, AbstractUser))
        self.assertTrue(issubclass(self.model, UUIDModel))
