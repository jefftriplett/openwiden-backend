from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
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

    @swagger_auto_schema(request_body=None)
    @action(detail=True, methods=["POST"])
    def add(self, request: Request, **kwargs) -> Response:
        repository = self.get_object()
        services.add_repository(repository=repository, user=request.user)
        return Response({"detail": "ok"})

    @action(detail=True, methods=["DELETE"])
    def remove(self, request: Request, **kwargs) -> Response:
        repository = self.get_object()
        services.remove_repository(repository=repository, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
