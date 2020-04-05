from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_q.tasks import async_task

from repositories import models, serializers, exceptions, filters, utils, tasks


class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.RepositorySerializer
    queryset = models.Repository.objects.all()
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)
    filterset_class = filters.Repository

    @action(detail=False, methods=["POST"], permission_classes=(permissions.IsAuthenticated,))
    def add(self, request, *args, **kwargs):
        url = request.data["url"]
        parsed_url = utils.parse_repo_url(url)

        if parsed_url is None:
            raise exceptions.RepositoryURLParse(url)

        try:
            service = models.VersionControlService.objects.get(host=parsed_url.host)
        except models.VersionControlService.DoesNotExist:
            raise exceptions.VersionControlServiceNotFound(parsed_url.host)

        if service.host == "github.com":
            async_task(tasks.add_github_repository, self.request.user, parsed_url, service)
        elif service.host == "gitlab.com":
            async_task(tasks.add_gitlab_repository, self.request.user, parsed_url, service)
        else:
            return Response({"detail": _(f"Not implemented yet.")}, status=status.HTTP_501_NOT_IMPLEMENTED)

        return Response({"detail": _("Thank you! Repository will be added soon, you will be notified by e-mail.")})


class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.IssueSerializer
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return models.Issue.objects.filter(repository=self.kwargs["repository_id"])


class ProgrammingLanguage(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ProgrammingLanguage
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)
    queryset = models.ProgrammingLanguage.objects.all()
