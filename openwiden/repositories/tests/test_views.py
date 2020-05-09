from unittest import mock

import pytest
from django.http import Http404
from rest_framework import permissions

from openwiden.repositories import views, serializers, filters, models, error_messages

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

    def test_get_queryset(self, create_repository, create_issue, monkeypatch):
        repo = create_repository()
        repo_id = str(repo.id)
        issue = create_issue(repository=repo)
        view = self.view_cls()
        view.kwargs = dict(repository_id=repo_id)

        qs = view.get_queryset()

        assert qs.count() == 1
        assert qs.first().id == issue.id

        def raise_does_not_exist(**kwargs):
            raise models.Repository.DoesNotExist

        monkeypatch.setattr(views.models.Repository.objects, "get", raise_does_not_exist)

        with pytest.raises(Http404) as e:
            view.get_queryset()
            assert e.value == error_messages.REPOSITORY_DOES_NOT_EXIST.format(id=repo_id)


class TestUserRepositoriesViewSet:
    view_cls = views.UserRepositories

    @mock.patch.object(views.services.Repository, "get_user_repos")
    def test_get_queryset(self, patched_get_user_repos, api_rf, mock_user):
        qs = models.Repository.objects.none()
        patched_get_user_repos.return_value = qs
        view = self.view_cls()
        request = api_rf.get("/fake-url/")
        request.user = mock_user
        view.request = request

        assert view.get_queryset() == qs

    @mock.patch.object(views.UserRepositories, "get_object")
    @mock.patch.object(views.services.Repository, "add")
    def test_add(self, patched_add, patched_get_obj, api_rf, mock_user, mock_repo):
        task_id = "1"
        patched_get_obj.return_value = mock_repo
        patched_add.return_value = task_id

        view = self.view_cls()
        request = api_rf.post("/fake-url/")
        request.user = mock_user

        response = view.add(request)

        assert response.status_code == 200
        assert response.data == {"task_id": task_id}

        patched_add.side_effect = views.ServiceException("test")

        response = view.add(request)

        assert response.status_code == 400
        assert response.data == "test"

        assert patched_add.call_count == 2
        assert patched_get_obj.call_count == 2
