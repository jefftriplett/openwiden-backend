from unittest import mock

import pytest
from rest_framework.response import Response
from rest_framework.reverse import reverse

from openwiden import enums
from openwiden.users import views, serializers, services
from openwiden.users.exceptions import GitLabOAuthMissedRedirectURI


pytestmark = pytest.mark.django_db


class MockClient:
    @staticmethod
    def authorize_redirect(*args, **kwargs):
        return Response("http://fake-redirect.com/", 302)


@mock.patch.object(services, "get_client")
def test_oauth_login_view(patched_get_client, api_rf):
    patched_get_client.return_value = MockClient

    view = views.OAuthLoginView()
    request = api_rf.get("/fake-url/")

    response = view.get(request, enums.VersionControlService.GITHUB.value)

    assert response.status_code == 302

    with pytest.raises(GitLabOAuthMissedRedirectURI) as e:
        view.get(request, enums.VersionControlService.GITLAB)

    assert e.value.detail == GitLabOAuthMissedRedirectURI().detail

    request = api_rf.get("/fake-url/?redirect_uri=http://example.com")

    response = view.get(request, enums.VersionControlService.GITLAB)
    assert response.status_code == 302


@mock.patch.object(services, "get_jwt_tokens")
@mock.patch.object(services, "oauth")
def test_oauth_complete_view(
    patched_oauth, patched_get_jwt_tokens, api_rf, monkeypatch, mock_user,
):
    mock_jwt_tokens = dict(access="12345", refresh="67890")

    patched_oauth.return_value = mock_user
    patched_get_jwt_tokens.return_value = mock_jwt_tokens

    view = views.OAuthCompleteView()
    request = api_rf.get("/fake-url/")
    request.user = mock_user
    view.request = request

    response = view.get(request, enums.VersionControlService.GITHUB.value)

    assert response.status_code == 200
    assert response.data == mock_jwt_tokens


class TestUserViewSet:
    def test_get_serializer_cls(self, api_rf):
        view = views.UserViewSet()
        view.action = "list"

        assert view.get_serializer_class() == view.serializer_class

        view.action = "update"

        assert view.get_serializer_class() == serializers.UserUpdateSerializer

    # def test_me(self, api_rf, monkeypatch, mock_user):
    #     monkeypatch.setattr(views.serializers.UserWithVCSAccountsSerializer, "data", {})
    #
    #     view = views.UserViewSet()
    #     request = api_rf.get("/fake-url/")
    #     request.user = mock_user
    #
    #     response = view.me(request)
    #
    #     assert response.status_code == 200
    #     assert response.data == {}

    def test_me_anonymous_user(self, client):
        response = client.get(reverse("api-v1:user-me"))

        assert response.status_code == 403
