from django.test import TestCase
from repositories.models import Repository

from . import factories


class RepositoryManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.version_control_service = factories.VersionControlService.create()
        cls.repository = factories.Repository.build()
        cls.issues = factories.Issue.build_batch(3)

    def create_repository(self, **override_kwargs) -> Repository:
        kwargs = dict(
            version_control_service=self.version_control_service,
            remote_id=self.repository.remote_id,
            name=self.repository.name,
            description=self.repository.description,
            url=self.repository.url,
            forks_count=self.repository.forks_count,
            star_count=self.repository.star_count,
            created_at=self.repository.created_at,
            updated_at=self.repository.updated_at,
            programming_languages=self.repository.programming_languages,
            issues=[
                dict(
                    remote_id=i.remote_id,
                    title=i.title,
                    description=i.description,
                    state=i.state,
                    labels=i.labels,
                    url=i.url,
                    created_at=i.created_at,
                    closed_at=i.closed_at,
                    updated_at=i.updated_at,
                )
                for i in self.issues
            ],
        )

        if override_kwargs:
            kwargs.update(override_kwargs)

        return Repository.objects.nested_create(**kwargs)

    def test_nested_create_full(self):
        self.create_repository()

    def test_nested_create_default_programming_languages(self):
        self.create_repository(programming_languages=None)

    def test_nested_create_no_issues(self):
        self.create_repository(issues=[])
