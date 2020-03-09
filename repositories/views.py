from django.conf import settings
from django.utils.timezone import make_aware
from github import Github

from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .exceptions import RepositoryURLParse, PrivateRepository
from .models import Repository, VersionControlService
from .serializers import RepositorySerializer
from .utils import parse_repo_url


github = Github(client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_SECRET_KEY)


class RepositoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)

    @action(detail=False, methods=["POST"])
    def add(self, request, *args, **kwargs):
        url = request.data["url"]
        service_label, repo_name = parse_repo_url(url)

        if service_label is None or repo_name is None:
            raise RepositoryURLParse(url)

        service = get_object_or_404(VersionControlService.objects.all(), label=service_label)
        data = None

        if service_label == "github":
            repo = github.get_repo(repo_name)

            if repo.private:
                raise PrivateRepository()

            defaults = {
                "name": repo.name,
                "description": repo.description,
                "url": repo.html_url,
                "forks_count": repo.forks_count,
                "star_count": repo.stargazers_count,
                "created_at": make_aware(repo.created_at),
                "updated_at": make_aware(repo.updated_at),
                "open_issues_count": repo.open_issues_count,
            }
            repository, created = Repository.objects.update_or_create(
                version_control_service=service, remote_id=repo.id, defaults=defaults,
            )
            data = self.serializer_class(repository).data

        return Response(data)
