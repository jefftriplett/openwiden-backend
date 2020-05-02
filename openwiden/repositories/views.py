from rest_framework import viewsets, permissions

from openwiden.repositories import serializers, models, filters


class Repository(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Repository
    queryset = models.Repository.objects.all()
    filterset_class = filters.Repository
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"


class Issue(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Issue
    lookup_field = "id"
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return models.Issue.objects.filter(repository=self.kwargs["repository_id"])
