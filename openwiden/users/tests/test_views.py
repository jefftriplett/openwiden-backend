import pytest
from rest_framework.response import Response

from openwiden import enums, exceptions
from openwiden.users import views, serializers
from openwiden.users.exceptions import GitLabOAuthMissedRedirectURI
from openwiden.services.oauth import OAuthService


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
        vcs = enums.VersionControlService.GITHUB
        settings.AUTHLIB_OAUTH_CLIENTS = {vcs: authlib_settings_github}

        client = views.OAuthLoginView.get_client(vcs)

        assert client.name == vcs

    def test_get_client_raises_service_exception(self, settings):
        settings.AUTHLIB_OAUTH_CLIENTS = {}
        vcs = "test"

        with pytest.raises(exceptions.ServiceException) as e:
            views.OAuthLoginView.get_client(vcs)
            assert e.value == exceptions.ServiceException(vcs).description

    def test_get(self, api_rf, monkeypatch):
        monkeypatch.setattr(views.OAuthLoginView, "get_client", MockClient.get_mock_client)

        view = views.OAuthLoginView()
        request = api_rf.get("/fake-url/")

        response = view.get(request, "vcs")

        assert response.status_code == 302

        with pytest.raises(GitLabOAuthMissedRedirectURI) as e:
            view.get(request, enums.VersionControlService.GITLAB)
            assert e.value == GitLabOAuthMissedRedirectURI().detail

        request = api_rf.get("/fake-url/?redirect_uri=http://example.com")

        response = view.get(request, enums.VersionControlService.GITLAB)
        assert response.status_code == 302


def test_oauth_complete_view(api_rf, monkeypatch, mock_user):
    def return_mock_user(*args):
        return mock_user

    mock_jwt_tokens = dict(access="12345", refresh="67890")

    def return_mock_jwt_tokens(*args):
        return mock_jwt_tokens

    monkeypatch.setattr(OAuthService, "oauth", return_mock_user)
    monkeypatch.setattr(views.services.UserService, "get_jwt", return_mock_jwt_tokens)

    view = views.OAuthCompleteView()
    request = api_rf.get("/fake-url/")
    request.user = mock_user
    view.request = request

    response = view.get(request, "vcs")

    assert response.status_code == 200
    assert response.data == mock_jwt_tokens

    def raise_remote_exception(*args):
        raise exceptions.ServiceException("description")

    monkeypatch.setattr(OAuthService, "oauth", raise_remote_exception)

    with pytest.raises(exceptions.ServiceException) as e:
        response = view.get(request, "vcs")

        assert e.value == "description"
        assert response.status_code == 400
        assert response.data == {"detail": "description"}


class TestUserViewSet:
    def test_get_serializer_cls(self, api_rf):
        view = views.UserViewSet()
        view.action = "list"

        assert view.get_serializer_class() == view.serializer_class

        view.action = "update"

        assert view.get_serializer_class() == serializers.UserUpdateSerializer

    def test_me(self, api_rf, monkeypatch, mock_user):
        monkeypatch.setattr(views.serializers.UserWithVCSAccountsSerializer, "data", {})

        view = views.UserViewSet()
        request = api_rf.get("/fake-url/")
        request.user = mock_user

        response = view.me(request)

        assert response.status_code == 200
        assert response.data == {}
