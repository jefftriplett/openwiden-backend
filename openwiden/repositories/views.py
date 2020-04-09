from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_q.tasks import async_task

from openwiden.repositories import serializers, tasks, models, exceptions, filters, utils


class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    queryset = models.Repository.objects.all().select_related("programming_language")
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)
    filterset_class = filters.Repository

    @action(detail=False, methods=["POST"], permission_classes=(permissions.IsAuthenticated,))
    def add(self, request, *args, **kwargs):
        url = request.data["url"]
        parsed_url = utils.parse_repo_url(url)

        # If repository url was not parsed (None returned)
        if parsed_url is None:
            raise exceptions.RepositoryURLParse(url)

        # Try to find version control service by url host
        try:
            service = models.VersionControlService.objects.get(host=parsed_url.host)
        except models.VersionControlService.DoesNotExist:
            raise exceptions.VersionControlServiceNotFound(parsed_url.host)

        async_task(tasks.update_or_create_repository, self.request.user, service, parsed_url.owner, parsed_url.repo)

        return Response({"detail": _("Thank you! Repository will be added soon, you will be notified by e-mail.")})


class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Issue
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return models.Issue.objects.filter(repository=self.kwargs["repository_id"])


class ProgrammingLanguage(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ProgrammingLanguage
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)
    queryset = models.ProgrammingLanguage.objects.all()
