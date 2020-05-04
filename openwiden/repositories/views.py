from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from openwiden.repositories import serializers, models, filters, services
from openwiden.services.exceptions import ServiceException


class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    queryset = services.Repository.added_and_public()
    filterset_class = filters.Repository
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"


class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Issue
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return models.Issue.objects.filter(repository=self.kwargs["repository_id"])


class UserRepositories(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    lookup_field = "id"
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return services.Repository.get_user_repos(self.request.user)

    @action(detail=True, methods=["POST"])
    def add(self, request, *args, **kwargs):
        repository = self.get_object()
        try:
            task_id = services.Repository.add(repository=repository, user=self.request.user)
        except ServiceException as e:
            return Response(e.description, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"task_id": task_id})
