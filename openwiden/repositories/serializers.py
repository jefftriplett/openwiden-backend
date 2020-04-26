from rest_framework import serializers

from openwiden.repositories import models


# class ProgrammingLanguage(serializers.ModelSerializer):
#     class Meta:
#         model = models.ProgrammingLanguage
#         fields = ("id", "name")


class Repository(serializers.ModelSerializer):
    version_control_service = serializers.CharField(source="version_control_service.host")
    # programming_language = ProgrammingLanguage()

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
            # "programming_language",
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
