import pytest
from rest_framework.response import Response

from openwiden import enums
from openwiden.users import views, exceptions


pytestmark = pytest.mark.django_db


class MockClient:
    @staticmethod
    def authorize_redirect(request, redirect_uri):
        return Response("http://fake-redirect.com/", 302)

    @staticmethod
    def get_mock_client(self, provider):
        return MockClient()


class TestOAuthLoginView:
    def test_get_client_success(self, settings, authlib_settings_github):
        provider = enums.VersionControlService.GITHUB
        settings.AUTHLIB_OAUTH_CLIENTS = {provider: authlib_settings_github}

        client = views.OAuthLoginView.get_client(provider)

        assert client.name == provider

    def test_get_client_raises_oauth_provider_not_found(self, settings):
        settings.AUTHLIB_OAUTH_CLIENTS = {}
        provider = "test"

        with pytest.raises(exceptions.OAuthProviderNotFound) as e:
            views.OAuthLoginView.get_client(provider)
            assert e.value == exceptions.OAuthProviderNotFound(provider).detail

    def test_get(self, api_rf, user, settings, authlib_settings_gitlab, authlib_settings_github, monkeypatch):
        monkeypatch.setattr(views.OAuthLoginView, "get_client", MockClient.get_mock_client)

        view = views.OAuthLoginView()
        request = api_rf.get("fake")
        request.user = user
        view.request = request
        settings.AUTHLIB_OAUTH_CLIENTS = {"github": authlib_settings_github, "gitlab": authlib_settings_gitlab}

        response = view.get(request, enums.VersionControlService.GITHUB)

        assert response.status_code == 302

        with pytest.raises(exceptions.GitLabOAuthMissedRedirectURI) as e:
            view.get(request, enums.VersionControlService.GITLAB)

            assert e.value == exceptions.GitLabOAuthMissedRedirectURI().detail


# @override_settings(AUTHLIB_OAUTH_CLIENTS={"github": fixtures.GITHUB_PROVIDER, "gitlab": fixtures.GITLAB_PROVIDER})
# class OAuthCompleteViewTestCase(ViewTestCase):
#     url_namespace = "auth:complete"
#
#     @mock.patch("openwiden.users.services.oauth.OAuthService.get_profile")
#     def test_raises_get_profile_exception(self, p_get_profile):
#         p_get_profile.side_effect = service_exceptions.ProfileRetrieveException("test")
#         url = self.get_url(provider="test")
#         r = self.client.get(url)
#         self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(r.data, {"detail": str(service_exceptions.ProfileRetrieveException("test"))})
#         self.assertEqual(p_get_profile.call_count, 1)
#
#     @mock.patch("openwiden.users.services.user.UserService.get_jwt")
#     @mock.patch("openwiden.users.services.oauth.OAuthService.oauth")
#     def test_success(self, p_oauth, p_get_jwt):
#         user = factories.UserFactory.create()
#         expected_jwt = {"access": "123", "refresh": "123"}
#         p_oauth.return_value = user
#         p_get_jwt.return_value = expected_jwt
#         mock_client = mock.MagicMock()
#         profile = fixtures.create_random_profile()
#         mock_client.get.return_value = profile
#         url = self.get_url(provider="github")
#         r = self.client.get(url)
#         self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
#         self.assertEqual(r.data, expected_jwt)
#         self.assertEqual(p_oauth.call_count, 1)
#         self.assertEqual(p_get_jwt.call_count, 1)
#
#
# class UsersViewSetTestCase(ViewTestCase):
#     url_namespace = "user"
#
#     def setUp(self) -> None:
#         self.user = factories.UserFactory.create()
#         self.set_auth_header(self.user)
#
#     def test_list(self):
#         url = self.get_url(postfix="list")
#         r = self.client.get(url)
#         self.assertEqual(r.status_code, status.HTTP_200_OK)
#         first_result = r.data["results"][0]
#         self.assertEqual(first_result["id"], self.user.id)
#         self.assertEqual(first_result["username"], self.user.username)
#
#     def test_detail(self):
#         url = self.get_url(postfix="detail", id=self.user.id)
#         r = self.client.get(url)
#         self.assertEqual(r.status_code, status.HTTP_200_OK)
#
#     def test_update(self):
#         username = fake.user_name()
#         first_name = fake.first_name()
#         last_name = fake.last_name()
#         data = {"username": username, "first_name": first_name, "last_name": last_name}
#         url = self.get_url(postfix="detail", id=self.user.id)
#         r = self.client.patch(url, data=data)
#         self.assertEqual(r.status_code, status.HTTP_200_OK)
#         self.assertEqual(r.data["first_name"], first_name)
#
#     def test_create(self):
#         url = self.get_url(postfix="list")
#         r = self.client.post(url)
#         self.assertEqual(r.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
#
#
# class UserRetrieveByTokenViewTestCase(ViewTestCase):
#     url_namespace = "user"
#
#     def test_success(self):
#         user = factories.UserFactory.create()
#         factories.OAuth2TokenFactory.create(user=user, provider="github")
#         factories.OAuth2TokenFactory.create(user=user, provider="gitlab")
#         self.set_auth_header(user)
#
#         expected_data = serializers.UserWithOAuthTokensSerializer(user).data
#         mock_get = mock.MagicMock("users.views.UserWithOAuthTokensSerializer.data")
#         mock_get.return_value = expected_data
#         r = self.client.get(self.get_url())
#
#         self.assertEqual(r.status_code, status.HTTP_200_OK)
#         self.assertEqual(r.data, expected_data)
#         self.assertEqual(len(r.data["oauth2_tokens"]), 2)
