from django.test import TestCase

from openwiden.users.apps import UsersConfig
from django.utils.translation import gettext_lazy as _


class UsersAppTestCase(TestCase):
    def test_config_attrs(self):
        self.assertEqual(UsersConfig.name, "openwiden.users")
        self.assertEqual(UsersConfig.label, "users")
        self.assertEqual(UsersConfig.verbose_name, _("users"))
