from django_q.tasks import async_task
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from openwiden.repositories import serializers, models, filters, services
from openwiden.services.exceptions import ServiceException
from openwiden.users import services as users_services


class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    queryset = models.Repository.objects.all()
    filterset_class = filters.Repository
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"

    @action(detail=True, methods=["POST"])
    def add(self, request, *args, **kwargs):
        repository = self.get_object()
        try:
            oauth_token = users_services.OAuthToken.get_token(self.request.user, repository.version_control_service)
        except ServiceException as e:
            return Response(e.description, status=status.HTTP_400_BAD_REQUEST)
        else:
            task_id = async_task(services.Repository.add, repository=repository, oauth_token=oauth_token)
            return Response({"task_id": task_id})


class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Issue
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return models.Issue.objects.filter(repository=self.kwargs["repository_id"])
