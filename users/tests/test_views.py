from urllib.parse import urlencode

import mock
from faker import Faker
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.exceptions import OAuthProviderNotFound, GitLabOAuthMissedRedirectURI

from .factories import UserFactory

fake = Faker()


GITHUB_PROVIDER = {
    "client_id": "GITHUB_CLIENT_ID",
    "client_secret": "GITHUB_SECRET_KEY",
    "access_token_url": "https://github.com/login/oauth/access_token",
    "access_token_params": None,
    "authorize_url": "https://github.com/login/oauth/authorize",
    "authorize_params": None,
    "api_base_url": "https://api.github.com/",
    "client_kwargs": {"scope": "user:email"},
}

GITLAB_PROVIDER = {
    "client_id": "GITHUB_CLIENT_ID",
    "client_secret": "GITHUB_SECRET_KEY",
    "access_token_url": "http://gitlab.example.com/oauth/token",
    "access_token_params": None,
    "authorize_url": "https://gitlab.example.com/oauth/authorize",
    "authorize_params": None,
    "api_base_url": "https://gitlab.example.com/api/v4/",
    "client_kwargs": None,
}


class Profile:
    id = fake.pyint()
    login = f"{fake.first_name()} {fake.last_name()}"
    name = fake.name()
    email = fake.email()

    def json(self):
        return {"id": self.id, "login": self.login, "name": self.name, "email": self.email}


class ProviderNotFoundTestMixin:

    url_path = None

    def test_client_not_found(self):
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "test_provider"}))
        detail = OAuthProviderNotFound("test_provider").detail
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"detail": detail}, response.data)


@override_settings(
    AUTHLIB_OAUTH_CLIENTS={"github": GITHUB_PROVIDER, "gitlab": GITLAB_PROVIDER,}
)
class OAuthLoginViewTestCase(APITestCase, ProviderNotFoundTestMixin):

    url_path = "users:login"

    def test_github_provider(self):
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "github"}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_gitlab_provider(self):
        url = reverse_lazy(self.url_path, kwargs={"provider": "gitlab"})
        response = self.client.get(f"{url}?redirect_uri=http://example.com/")
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_gitlab_provider_no_redirect_uri(self):
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "gitlab"}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": GitLabOAuthMissedRedirectURI().detail})

    def test_github_provider_redirect_uri_is_correct(self):
        redirect_uri = "http://localhost:3000/repositories/"
        query_params = urlencode({"redirect_uri": redirect_uri})
        url = reverse_lazy(self.url_path, kwargs={"provider": "github"}) + f"?{query_params}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertIn(query_params, response.url)


@override_settings(
    AUTHLIB_OAUTH_CLIENTS={"github": GITHUB_PROVIDER, "gitlab": GITLAB_PROVIDER,}
)
class OAuthCompleteViewTestCase(APITestCase, ProviderNotFoundTestMixin):

    url_path = "users:complete"

    def get_user_data(self, access_token) -> dict:
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
        response = self.client.get(reverse_lazy("user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION="")
        return response.data

    @mock.patch("authlib.integrations.base_client.base_app.BaseApp.get")
    @mock.patch("authlib.integrations.django_client.integration.DjangoRemoteApp.authorize_access_token")
    def test_github_provider(self, patched_authorize_access_token, get_patched):
        profile = Profile()
        patched_authorize_access_token.return_value = {
            "access_token": "12345",
            "token_type": "bearer",
            "scope": "user:email",
        }
        get_patched.return_value = profile
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "github"}))

        access_token = response.data["detail"]["access"]

        self.assertTrue(patched_authorize_access_token.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)

        # Get current user by retrieved tokens
        user_data = self.get_user_data(access_token)
        self.assertEqual(user_data["username"], profile.login)
        self.assertEqual(user_data["email"], profile.email)
        user_id = user_data["id"]

        # Try to create user again with anonymous user
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "github"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        access_token = response.data["detail"]["access"]

        # Check that returned user is the same as created before
        user_data = self.get_user_data(access_token)
        self.assertEqual(user_data["id"], user_id)
        self.assertEqual(user_data["username"], profile.login)
        self.assertEqual(user_data["email"], profile.email)


class UsersViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        access_token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")

    def test_list_view(self):
        response = self.client.get(reverse_lazy("users:user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_result = response.data["results"][0]
        self.assertEqual(first_result["id"], self.user.id)
        self.assertEqual(first_result["username"], self.user.username)

    def test_detail_view(self):
        response = self.client.get(reverse_lazy("users:user-detail", kwargs={"id": self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_view(self):
        first_name = fake.first_name()
        data = {"first_name": first_name}
        response = self.client.patch(reverse_lazy("users:user-detail", kwargs={"id": self.user.id}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], first_name)

    def test_delete_view(self):
        response = self.client.delete(reverse_lazy("users:user-detail", kwargs={"id": self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user._meta.model.objects.filter(id=self.user.id).exists())

    def test_create_view(self):
        response = self.client.post(reverse_lazy("users:user-list"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
