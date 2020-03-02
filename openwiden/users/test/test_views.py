from unittest import mock

import factory
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from faker import Faker
from nose.tools import eq_, ok_
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from openwiden.users.test.factories import UserFactory
from openwiden.users import github_oauth


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
        response: Response = self.client.post(self.url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.data)

    @mock.patch("openwiden.users.views.github.fetch_token")
    def test_post_request_with_valid_data_success(self, patched):
        patched.return_value = fake.pystr(min_chars=40, max_chars=40)
        data = {"code": fake.pystr(min_chars=20, max_chars=20)}
        response = self.client.post(self.url, data=data)
        user = User.objects.get(id=response.data.get("id"))

        eq_(patched.call_count, 1)
        eq_(response.status_code, status.HTTP_201_CREATED, msg=response.data)
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


class TestUserExtraActionTestCase(APITestCase):
    """
    Tests user get_auth_url extra action.
    """

    def setUp(self) -> None:
        self.url = reverse("user-auth")

    def test_get_auth_url_redirects_to_a_valid_url(self):
        response: HttpResponseRedirect = self.client.get(self.url)
        github = github_oauth.GitHubOAuth(
            settings.GITHUB_KEY, settings.GITHUB_SECRET, ["user:email"]
        )
        auth_url = github.authorization_url

        self.assertRedirects(
            response, auth_url, fetch_redirect_response=False,
        )
