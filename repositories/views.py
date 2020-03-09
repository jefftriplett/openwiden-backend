from rest_framework import viewsets, mixins, permissions

from .models import Repository
from .serializers import RepositorySerializer


class RepositoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = RepositorySerializer
    queryset = Repository.objects.all()
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)
