import mock
from urllib.parse import urlencode
from authlib.common.errors import AuthlibBaseError
from faker import Faker
from django.test import override_settings
from rest_framework import status

from openwiden.users import exceptions, serializers
from openwiden.users.tests.factories import UserFactory, OAuth2TokenFactory
from openwiden.tests.cases import ViewTestCase

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


# class ProviderNotFoundTestMixin(APITestCase):
#     url_path = None

# def test_client_not_found(self):
#     response = self.client.get(reverse_lazy(self.url_path, kwargs={"provider": "test_provider"}))
#     detail = exceptions.OAuthProviderNotFound("test_provider").detail
#     self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
#     self.assertEqual({"detail": detail}, response.data)


@override_settings(AUTHLIB_OAUTH_CLIENTS={"github": GITHUB_PROVIDER, "gitlab": GITLAB_PROVIDER})
class OAuthLoginViewTestCase(ViewTestCase):
    url_namespace = "auth:login"

    @mock.patch("openwiden.users.utils.requests.get")
    def test_github_provider(self, p):
        p.return_value = "test"
        url = self.get_url(provider="github")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_302_FOUND)

    @mock.patch("openwiden.users.utils.requests.get")
    def test_gitlab_provider(self, p):
        p.return_value = "test"
        url = self.get_url(query=dict(redirect_uri="http://example.com/"), provider="gitlab")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_302_FOUND)

    def test_gitlab_provider_no_redirect_uri(self):
        url = self.get_url(provider="gitlab")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, {"detail": exceptions.GitLabOAuthMissedRedirectURI().detail})

    def test_github_provider_redirect_uri_is_correct(self):
        redirect_uri = "http://localhost:3000/repositories/"
        query = {"redirect_uri": redirect_uri}
        query_params = urlencode(query)
        url = self.get_url(query=query, provider="github")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_302_FOUND)
        self.assertIn(query_params, r.url)


@override_settings(AUTHLIB_OAUTH_CLIENTS={"github": GITHUB_PROVIDER, "gitlab": GITLAB_PROVIDER})
class OAuthCompleteViewTestCase(ViewTestCase):
    url_namespace = "auth:complete"

    @mock.patch("openwiden.users.views.create_or_update_user")
    @mock.patch("openwiden.users.views.oauth.create_client")
    def test_raises_error_when_user_is_none(self, patched_create_client, patched_create_or_update_user):
        patched_create_client.return_value = "test"
        patched_create_or_update_user.return_value = None
        url = self.get_url(provider="test")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, {"detail": exceptions.CreateOrUpdateUserReturnedNone().detail})

    @mock.patch("openwiden.users.views.create_or_update_user")
    @mock.patch("openwiden.users.views.oauth.create_client")
    def test_raises_authlib_error(self, patched_create_client, patched_create_or_update_user):
        patched_create_client.return_value = "test"
        patched_create_or_update_user.side_effect = AuthlibBaseError(description="test error")
        url = self.get_url(provider="test")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, {"detail": "test error"})

    @mock.patch("openwiden.users.views.create_or_update_user")
    @mock.patch("openwiden.users.views.oauth.create_client")
    def test_returns_tokens(self, patched_create_client, patched_create_or_update_user):
        user = UserFactory.create()
        patched_create_client.return_value = "test"
        patched_create_or_update_user.return_value = user
        url = self.get_url(provider="test")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("access", r.data["detail"])
        self.assertIn("refresh", r.data["detail"])


class UsersViewSetTestCase(ViewTestCase):
    url_namespace = "user"

    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.set_auth_header(self.user)

    def test_list(self):
        url = self.get_url(postfix="list")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        first_result = r.data["results"][0]
        self.assertEqual(first_result["id"], self.user.id)
        self.assertEqual(first_result["username"], self.user.username)

    def test_detail(self):
        url = self.get_url(postfix="detail", id=self.user.id)
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_update(self):
        username = fake.user_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        data = {"username": username, "first_name": first_name, "last_name": last_name}
        url = self.get_url(postfix="detail", id=self.user.id)
        r = self.client.patch(url, data=data)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["first_name"], first_name)

    def test_create(self):
        url = self.get_url(postfix="list")
        r = self.client.post(url)
        self.assertEqual(r.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserRetrieveByTokenViewTestCase(ViewTestCase):
    url_namespace = "user"

    def test_success(self):
        user = UserFactory.create()
        OAuth2TokenFactory.create(user=user, provider="github")
        OAuth2TokenFactory.create(user=user, provider="gitlab")
        self.set_auth_header(user)

        expected_data = serializers.UserWithOAuthTokensSerializer(user).data
        mock_get = mock.MagicMock("users.views.UserWithOAuthTokensSerializer.data")
        mock_get.return_value = expected_data
        r = self.client.get(self.get_url())

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data, expected_data)
        self.assertEqual(len(r.data["oauth2_tokens"]), 2)
