from urllib.parse import urlencode

import mock
from authlib.common.errors import AuthlibBaseError
from faker import Faker
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.exceptions import OAuthProviderNotFound, GitLabOAuthMissedRedirectURI, CreateOrUpdateUserReturnedNone
from users.serializers import UserWithOAuthTokensSerializer

from .factories import UserFactory, OAuth2TokenFactory

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
    avatar_url = "https://test.com/avatar.jpg"

    def json(self):
        return {
            "id": self.id,
            "login": self.login,
            "name": self.name,
            "email": self.email,
            "avatar_url": self.avatar_url,
        }


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

    url_path = "auth:login"

    @mock.patch("users.utils.requests.get")
    def test_github_provider(self, p):
        p.return_value = "test"
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "github"}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    @mock.patch("users.utils.requests.get")
    def test_gitlab_provider(self, p):
        p.return_value = "test"
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

    url_path = "auth:complete"

    def get_user_data(self, access_token) -> dict:
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
        response = self.client.get(reverse_lazy("user"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION="")
        return response.data

    @mock.patch("users.views.create_or_update_user")
    @mock.patch("users.views.oauth.create_client")
    def test_raises_error_when_user_is_none(self, patched_create_client, patched_create_or_update_user):
        patched_create_client.return_value = "test"
        patched_create_or_update_user.return_value = None
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "test"}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": CreateOrUpdateUserReturnedNone().detail})

    @mock.patch("users.views.create_or_update_user")
    @mock.patch("users.views.oauth.create_client")
    def test_raises_authlib_error(self, patched_create_client, patched_create_or_update_user):
        patched_create_client.return_value = "test"
        patched_create_or_update_user.side_effect = AuthlibBaseError(description="test error")
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "test"}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "test error"})

    @mock.patch("users.views.create_or_update_user")
    @mock.patch("users.views.oauth.create_client")
    def test_returns_tokens(self, patched_create_client, patched_create_or_update_user):
        user = UserFactory.create()
        patched_create_client.return_value = "test"
        patched_create_or_update_user.return_value = user
        response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "test"}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["detail"])
        self.assertIn("refresh", response.data["detail"])


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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_view(self):
        username = fake.user_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        data = {"username": username, "first_name": first_name, "last_name": last_name}
        response = self.client.patch(reverse_lazy("users:user-detail", kwargs={"id": self.user.id}), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], first_name)

    def test_create_view(self):
        response = self.client.post(reverse_lazy("users:user-list"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserRetrieveByTokenViewTestCase(APITestCase):
    def test_get_action(self):
        user = UserFactory.create()
        OAuth2TokenFactory.create(user=user, provider="github")
        OAuth2TokenFactory.create(user=user, provider="gitlab")
        access_token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
        expected_data = UserWithOAuthTokensSerializer(user).data
        mock_get = mock.MagicMock("users.views.UserWithOAuthTokensSerializer.data")
        mock_get.return_value = expected_data
        response = self.client.get(reverse_lazy("user"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
        self.assertEqual(len(response.data["oauth2_tokens"]), 2)
