from rest_framework import serializers

from openwiden.repositories import models


class Repository(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        fields = (
            "id",
            "vcs",
            "name",
            "description",
            "url",
            "stars_count",
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


class UserRepository(Repository):
    class Meta(Repository.Meta):
        fields = Repository.Meta.fields + ("visibility", "is_added")
