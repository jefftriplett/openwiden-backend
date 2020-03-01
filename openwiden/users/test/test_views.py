import factory
from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Faker
from nose.tools import eq_, ok_
from rest_framework import status
from rest_framework.test import APITestCase

from openwiden.users.test.factories import UserFactory


fake = Faker()
User = get_user_model()


class TestUserListTestCase(APITestCase):
    """
    Tests users-list actions.
    """

    def setUp(self):
        self.url = reverse("user-list")
        self.user_data = factory.build(dict, FACTORY_CLASS=UserFactory)

    def test_post_request_with_no_data_fails(self):
        response = self.client.post(self.url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        response = self.client.post(self.url, {"code": "test_code"})
        eq_(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(id=response.data.get("id"))
        eq_(user.username, self.user_data.get("username"))
        ok_(user.github_token)


class TestUserDetailTestCase(APITestCase):
    """
    Tests user-list actions.
    """

    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse("user-detail", kwargs={"id": self.user.id})
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user.github_token}")

    def test_get_request_returns_user(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)

    def test_put_request_updates_user(self):
        new_first_name = fake.first_name()
        payload = {"first_name": new_first_name}
        response = self.client.put(self.url, payload)
        eq_(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=self.user.id)
        eq_(user.first_name, new_first_name)
