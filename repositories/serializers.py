from rest_framework import serializers

from .models import Repository, Issue


class RepositorySerializer(serializers.ModelSerializer):
    version_control_service = serializers.CharField(source="version_control_service.host")

    class Meta:
        model = Repository
        fields = (
            "id",
            "version_control_service",
            "name",
            "description",
            "url",
            "star_count",
            "open_issues_count",
            "forks_count",
            "created_at",
            "updated_at",
            "programming_languages",
        )


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "id",
            "title",
            "description",
            "state",
            "labels",
            "url",
            "created_at",
            "closed_at",
            "updated_at",
        )
