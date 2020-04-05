from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_q.tasks import async_task

from repositories import models, serializers
from .exceptions import RepositoryURLParse, VersionControlServiceNotFound
from .filters import RepositoryFilter
from .utils import parse_repo_url
from .tasks import add_github_repository, add_gitlab_repository


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.RepositorySerializer
    queryset = models.Repository.objects.all()
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)
    filterset_class = RepositoryFilter

    @action(detail=False, methods=["POST"], permission_classes=(permissions.IsAuthenticated,))
    def add(self, request, *args, **kwargs):
        url = request.data["url"]
        parsed_url = parse_repo_url(url)

        if parsed_url is None:
            raise RepositoryURLParse(url)

        try:
            service = models.VersionControlService.objects.get(host=parsed_url.host)
        except models.VersionControlService.DoesNotExist:
            raise VersionControlServiceNotFound(parsed_url.host)

        if service.host == "github.com":
            async_task(add_github_repository, self.request.user, parsed_url, service)
        elif service.host == "gitlab.com":
            async_task(add_gitlab_repository, self.request.user, parsed_url, service)
        else:
            return Response({"detail": _(f"Not implemented yet.")}, status=status.HTTP_501_NOT_IMPLEMENTED)

        return Response({"detail": _("Thank you! Repository will be added soon, you will be notified by e-mail.")})


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
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
