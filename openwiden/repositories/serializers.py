from rest_framework import serializers

from openwiden.repositories import models


class Repository(serializers.ModelSerializer):
    version_control_service = serializers.CharField()

    class Meta:
        model = models.Repository
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
        )


class Issue(serializers.ModelSerializer):
    class Meta:
        model = models.Issue
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
