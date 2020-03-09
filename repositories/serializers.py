from rest_framework import serializers

from .models import Repository


class RepositorySerializer(serializers.ModelSerializer):
    version_control_service_label = serializers.CharField(source="version_control_service.label")

    class Meta:
        model = Repository
        fields = (
            "id",
            "version_control_service_label",
            "name",
            "description",
            "url",
            "star_count",
            "open_issues_count",
            "forks_count",
            "created_at",
            "updated_at",
        )
