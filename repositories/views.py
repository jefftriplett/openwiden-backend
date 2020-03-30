from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from django_q.tasks import async_task

from .exceptions import RepositoryURLParse, VersionControlServiceNotFound
from .filters import RepositoryFilter
from .models import VersionControlService, Repository, Issue
from .serializers import RepositorySerializer, IssueSerializer
from .utils import parse_repo_url
from .tasks import add_github_repository


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()
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
            service = VersionControlService.objects.get(host=parsed_url.host)
        except VersionControlService.DoesNotExist:
            raise VersionControlServiceNotFound(parsed_url.host)

        if parsed_url.host.startswith("github"):
            async_task(add_github_repository, self.request.user, parsed_url, service)

        return Response({"detail": _("Thank you! Repository will be added soon, you will be notified by e-mail.")})


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IssueSerializer
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Issue.objects.filter(repository=self.kwargs["repository_id"])
