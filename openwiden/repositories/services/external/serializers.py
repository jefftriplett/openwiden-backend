from rest_framework import serializers

from openwiden.repositories import models, enums


class RepositorySync(serializers.ModelSerializer):
    class Meta:
        model = models.Repository
        exclude = ("version_control_service",)

    def create(self, validated_data):
        repository, created = self.Meta.model.objects.update_or_create(
            version_control_service=validated_data["version_control_service"],
            remote_id=validated_data["remote_id"],
            defaults=validated_data,
        )
        return repository


class GitHubRepositorySync(RepositorySync):
    class Meta(RepositorySync.Meta):
        pass

    def to_internal_value(self, data):
        """
        Note: visibility parameter is not yet implemented:
        https://developer.github.com/changes/2019-12-03-internal-visibility-changes/
        """
        data["remote_id"] = data.pop("id")
        data["visibility"] = enums.VisibilityLevel.private if data["private"] else enums.VisibilityLevel.public
        return super().to_internal_value(data)


class GitlabRepositorySync(RepositorySync):
    class Meta(RepositorySync.Meta):
        pass

    def to_internal_value(self, data):
        for new_key, key in (
            ("remote_id", "id"),
            ("url", "web_url"),
            ("updated_at", "last_activity_at"),
        ):
            data[new_key] = data.pop(key)
        return super().to_internal_value(data)
