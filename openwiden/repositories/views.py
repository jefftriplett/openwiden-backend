from django.http import Http404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from openwiden.repositories import serializers, models, filters, services, error_messages
from openwiden.services.exceptions import ServiceException


class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    queryset = services.Repository.added_and_public()
    filterset_class = filters.Repository
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"


class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Issue
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"

    def get_queryset(self):
        try:
            repository = models.Repository.objects.get(id=self.kwargs["repository_id"])
        except models.Repository.DoesNotExist:
            raise Http404(error_messages.REPOSITORY_DOES_NOT_EXIST.format(id=self.kwargs["repository_id"]))
        else:
            return repository.issues.all()


class UserRepositories(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.UserRepository
    lookup_field = "id"
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return services.Repository.get_user_repos(self.request.user)

    @action(detail=True, methods=["POST"])
    def add(self, request, **kwargs):
        repository = self.get_object()
        try:
            task_id = services.Repository.add(repo=repository, user=request.user)
        except ServiceException as e:
            return Response(e.description, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"task_id": task_id})
