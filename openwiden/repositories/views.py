from django.http import Http404
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from openwiden import exceptions

from . import serializers, filters, services, selectors


class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    queryset = selectors.get_added_and_public_repositories()
    filterset_class = filters.Repository
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"


class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Issue
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"

    def get_queryset(self):
        try:
            repository = selectors.get_repository(id=self.kwargs["repository_id"])
        except exceptions.ServiceException as e:
            raise Http404(e.description)
        else:
            return repository.issues.all()


class UserRepositories(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.UserRepository
    lookup_field = "id"
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return selectors.get_user_repositories(user=self.request.user)

    @action(detail=True, methods=["POST"])
    def add(self, request, **kwargs):
        repository = self.get_object()
        services.add_repository(repository=repository, user=request.user)
        return Response({"detail": "added."})
