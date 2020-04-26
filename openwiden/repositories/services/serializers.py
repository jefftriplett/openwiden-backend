from rest_framework import serializers

from openwiden.repositories import models


class GitHubRepository(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        fields = "__all__"

    def to_internal_value(self, data):
        data["remote_id"] = data.pop("id")
        return super().to_internal_value(data)


class GitlabRepository(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        fields = "__all__"

    def to_internal_value(self, data):
        for new_key, key in (
            ("remote_id", "id"),
            ("url", "web_url"),
            ("updated_at", "last_activity_at"),
        ):
            data[new_key] = data.pop(key)
        return super().to_internal_value(data)
