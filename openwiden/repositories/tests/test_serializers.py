import pytest

from openwiden.repositories import serializers, models

pytestmark = pytest.mark.django_db


class TestRepositorySerializer:
    def test_meta(self):
        assert serializers.Repository.Meta.model == models.Repository
        assert serializers.Repository.Meta.fields == (
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

    def test_to_representation(self, repository):
        serializers.Repository().to_representation(repository)


class TestIssueSerializer:
    def test_meta(self):
        assert serializers.Issue.Meta.model == models.Issue
        assert serializers.Issue.Meta.fields == (
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

    def test_to_representation(self, issue):
        serializers.Issue().to_representation(issue)


class TestUserRepositorySerializer:
    def test_meat(self):
        assert issubclass(serializers.UserRepository, serializers.Repository) is True
        assert serializers.UserRepository.Meta.fields == serializers.Repository.Meta.fields + ("visibility", "is_added")
