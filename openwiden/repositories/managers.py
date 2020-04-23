import typing as t
from openwiden.repositories import models
from django.db.models import Manager


class Repository(Manager):
    def update_or_create(
        self,
        version_control_service: "models.VersionControlService",
        remote_id,
        name,
        description,
        url,
        star_count,
        forks_count,
        open_issues_count,
        created_at,
        updated_at,
        programming_language: "models.ProgrammingLanguage",
    ) -> t.Tuple["models.Repository", bool]:
        return super().update_or_create(
            version_control_service=version_control_service,
            remote_id=remote_id,
            defaults=dict(
                name=name,
                description=description,
                url=url,
                star_count=star_count,
                forks_count=forks_count,
                open_issues_count=open_issues_count,
                created_at=created_at,
                updated_at=updated_at,
                programming_language=programming_language,
            ),
        )


class Issue(Manager):
    def update_or_create(
        self,
        repository: "models.Repository",
        remote_id,
        title,
        description,
        state,
        labels,
        url,
        created_at,
        updated_at,
    ) -> t.Tuple["models.Issue", bool]:
        return super().update_or_create(
            repository=repository,
            remote_id=remote_id,
            defaults=dict(
                title=title,
                description=description,
                state=state,
                labels=labels,
                url=url,
                created_at=created_at,
                updated_at=updated_at,
            ),
        )
