from typing import List

from django.db.models import Manager

from repositories import models


class RepositoryManager(Manager):
    def nested_create(
        self,
        version_control_service,
        remote_id,
        name,
        description,
        url,
        forks_count,
        star_count,
        created_at,
        updated_at,
        programming_languages: dict = None,
        issues: List[dict] = None,
    ):
        if programming_languages is None:
            programming_languages = {}

        repository = self.create(
            version_control_service=version_control_service,
            remote_id=remote_id,
            name=name,
            description=description,
            url=url,
            forks_count=forks_count,
            star_count=star_count,
            created_at=created_at,
            updated_at=updated_at,
            programming_languages=programming_languages,
        )

        if issues:
            models.Issue.objects.bulk_create([models.Issue(repository=repository, **i) for i in issues])
            repository.open_issues_count = repository.issues.filter(state=models.Issue.STATE_CHOICES.open).count()
            repository.save()

        return repository
