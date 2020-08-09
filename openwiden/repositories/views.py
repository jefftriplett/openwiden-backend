from django.utils.decorators import method_decorator
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from . import serializers, filters, services, selectors


@method_decorator(
    name="list", decorator=swagger_auto_schema(operation_summary="Get repositories list"),
)
@method_decorator(name="retrieve", decorator=swagger_auto_schema(operation_summary="Get repository by id"))
class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    queryset = selectors.get_added_repositories()
    filterset_class = filters.Repository
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"


@method_decorator(name="list", decorator=swagger_auto_schema(operation_summary="Get repository issues list"))
@method_decorator(name="retrieve", decorator=swagger_auto_schema(operation_summary="Get repository issue by id"))
class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Issue
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"

    def get_queryset(self):
        repository = selectors.get_repository(id=self.kwargs["repository_id"])
        return repository.issues.all()


@method_decorator(name="list", decorator=swagger_auto_schema(operation_summary="Get user repositories list"))
@method_decorator(name="retrieve", decorator=swagger_auto_schema(operation_summary="Get user repository by id"))
@method_decorator(
    name="add", decorator=swagger_auto_schema(operation_summary="Add user repository", request_body=no_body,)
)
@method_decorator(
    name="remove", decorator=swagger_auto_schema(operation_summary="Remove user repository"),
)
class UserRepositories(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.UserRepository
    lookup_field = "id"
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return selectors.get_user_repositories(user=self.request.user)

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
