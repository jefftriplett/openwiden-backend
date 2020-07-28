import logging

from rest_framework import serializers

from openwiden.enums import OwnerType
from openwiden.repositories import models

log = logging.getLogger(__name__)


class SyncIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Issue
        fields = (
            "remote_id",
            "title",
            "description",
            "state",
            "labels",
            "url",
            "created_at",
            "updated_at",
            "closed_at",
        )


class Repository(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

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
            "owner",
        )

    def get_owner(self, obj: models.Repository) -> dict:
        if obj.owner:
            return {
                "type": OwnerType.USER,
                "id": obj.owner.user.id,
                "name": obj.owner.login,
            }
        elif obj.organization:
            return {
                "type": OwnerType.ORGANIZATION,
                "id": obj.organization.id,
                "name": obj.organization.name,
            }
        else:
            raise ValueError(f"repository with id {obj.id} has no owner!")


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
