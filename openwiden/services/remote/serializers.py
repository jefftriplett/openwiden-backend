from rest_framework import serializers

from openwiden import enums
from openwiden.repositories import models as repositories_models
from openwiden.users import models as users_models
from openwiden.organizations import models as organization_models


class RepositorySync(serializers.ModelSerializer):
    class Meta:
        model = repositories_models.Repository
        fields = (
            "remote_id",
            "name",
            "description",
            "url",
            "star_count",
            "open_issues_count",
            "forks_count",
            "created_at",
            "updated_at",
            "visibility",
        )


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


class GitHubUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    avatar_url = serializers.URLField()


class GitlabUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    avatar_url = serializers.URLField()

    def to_internal_value(self, data):
        data["login"] = data.pop("username")
        return super().to_internal_value(data)


class OAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = users_models.OAuth2Token
        fields = "__all__"


class OrganizationSync(serializers.ModelSerializer):
    class Meta:
        model = organization_models.Organization
        fields = (
            "remote_id",
            "url",
            "avatar_url",
            "description",
            "name",
            "created_at",
            "visibility",
        )


class GithubOrganizationSync(OrganizationSync):
    class Meta(OrganizationSync.Meta):
        pass

    def to_internal_value(self, data):
        for new_key, old_key in {"remote_id": "id", "url": "html_url", "name": "login"}.items():
            data[new_key] = data.pop(old_key)
        return super().to_internal_value(data)


class GitlabOrganizationSync(OrganizationSync):
    class Meta(OrganizationSync.Meta):
        pass

    def to_internal_value(self, data):
        for new_key, old_key in {"remote_id": "id", "url": "web_url"}.items():
            data[new_key] = data.pop(old_key)
        return super().to_internal_value(data)
