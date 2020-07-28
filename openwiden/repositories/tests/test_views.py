from unittest import mock

import pytest
from rest_framework import permissions

from openwiden.repositories import views, serializers, filters, models, selectors

pytestmark = pytest.mark.django_db


class TestRepositoryViewSet:
    def test_attrs(self):
        view = views.Repository

        assert view.serializer_class == serializers.Repository
        assert view.filterset_class == filters.Repository
        assert view.permission_classes == (permissions.AllowAny,)
        assert view.lookup_field == "id"


class TestIssueViewSet:
    view_cls = views.Issue

    def test_attrs(self):
        assert self.view_cls.serializer_class == serializers.Issue
        assert self.view_cls.permission_classes == (permissions.AllowAny,)
        assert self.view_cls.lookup_field == "id"


class TestUserRepositoriesViewSet:
    view_cls = views.UserRepositories

    def test_attrs(self):
        assert self.view_cls.serializer_class == serializers.UserRepository
        assert self.view_cls.permission_classes == (permissions.IsAuthenticated,)
        assert self.view_cls.lookup_field == "id"

    @mock.patch.object(selectors, "get_user_repositories")
    def test_get_queryset(self, patched_get_user_repositories, api_rf, mock_user):
        qs = models.Repository.objects.none()
        patched_get_user_repositories.return_value = qs
        view = self.view_cls()
        request = api_rf.get("/fake-url/")
        request.user = mock_user
        view.request = request

        assert view.get_queryset() == qs
