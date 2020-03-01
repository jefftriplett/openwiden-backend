from django.test import TestCase
from nose.tools import eq_

from openwiden.users.test.factories import UserFactory


class UserModelTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_model_str_returns_username(self):
        eq_(str(self.user), self.user.username)
