import typing as t
from datetime import datetime

from openwiden.repositories import models


class Issue:
    @staticmethod
    def sync(
        repo: models.Repository,
        remote_id: int,
        title: str,
        description: str,
        state: str,
        labels: t.List[str],
        url: str,
        created_at: datetime,
        closed_at: datetime = None,
        updated_at: datetime = None,
    ) -> t.Tuple[models.Issue, bool]:
        """
        Synchronizes issue by specified data.
        """
        issue, created = models.Issue.objects.update_or_create(
            repository=repo,
            remote_id=remote_id,
            defaults=dict(
                title=title,
                description=description,
                state=state,
                labels=labels,
                url=url,
                created_at=created_at,
                closed_at=closed_at,
                updated_at=updated_at,
            ),
        )
        return issue, created
