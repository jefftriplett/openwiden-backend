from unittest import mock

from faker import Faker
from urllib.parse import urlencode
from django.test import override_settings
from rest_framework import status

from openwiden.users import exceptions, serializers, views
from openwiden.users.tests import factories, fixtures
from openwiden.tests.cases import ViewTestCase
from openwiden.users.services import exceptions as service_exceptions

fake = Faker()


@override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER, "gitlab": fixtures.GITLAB_PROVIDER})
class OAuthLoginViewTestCase(ViewTestCase):
    url_namespace = "auth:login"

    def test_oauth_provider_not_found(self):
        expected_message = exceptions.OAuthProviderNotFound("test").detail
        with self.assertRaisesMessage(exceptions.OAuthProviderNotFound, expected_message):
            views.OAuthLoginView.get_client("test")

    @mock.patch("openwiden.users.services.oauth.requests.get")
    def test_github_provider(self, p):
        p.return_value = "test"
        url = self.get_url(provider="github")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_302_FOUND)

    @mock.patch("openwiden.users.services.oauth.requests.get")
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


@override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER, "gitlab": fixtures.GITLAB_PROVIDER})
class OAuthCompleteViewTestCase(ViewTestCase):
    url_namespace = "auth:complete"

    @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
    def test_raises_get_profile_exception(self, p_get_profile):
        p_get_profile.side_effect = service_exceptions.ProfileRetrieveException("test")
        url = self.get_url(provider="test")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(r.data, {"detail": str(service_exceptions.ProfileRetrieveException("test"))})
        self.assertEqual(p_get_profile.call_count, 1)

    @mock.patch("openwiden.users.services.user.UserService.get_jwt")
    @mock.patch("openwiden.users.services.oauth.OAuthService.oauth")
    def test_success(self, p_oauth, p_get_jwt):
        user = factories.UserFactory.create()
        expected_jwt = {"access": "123", "refresh": "123"}
        p_oauth.return_value = user
        p_get_jwt.return_value = expected_jwt
        mock_client = mock.MagicMock()
        profile = fixtures.create_random_profile()
        mock_client.get.return_value = profile
        url = self.get_url(provider="github")
        r = self.client.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.assertEqual(r.data, expected_jwt)
        self.assertEqual(p_oauth.call_count, 1)
        self.assertEqual(p_get_jwt.call_count, 1)


class UsersViewSetTestCase(ViewTestCase):
    url_namespace = "user"

    def setUp(self) -> None:
        self.user = factories.UserFactory.create()
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
        user = factories.UserFactory.create()
        factories.OAuth2TokenFactory.create(user=user, provider="github")
        factories.OAuth2TokenFactory.create(user=user, provider="gitlab")
        self.set_auth_header(user)

        expected_data = serializers.UserWithOAuthTokensSerializer(user).data
        mock_get = mock.MagicMock("users.views.UserWithOAuthTokensSerializer.data")
        mock_get.return_value = expected_data
        r = self.client.get(self.get_url())

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data, expected_data)
        self.assertEqual(len(r.data["oauth2_tokens"]), 2)
