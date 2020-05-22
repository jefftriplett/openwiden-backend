import typing as t
from datetime import datetime

from openwiden.repositories import models, serializers
from openwiden import exceptions


class Issue:
    @classmethod
    def validate(cls, **kwargs) -> dict:
        serializer = serializers.SyncIssueSerializer(data=kwargs)
        if serializer.is_valid():
            return serializer.validated_data
        else:
            raise exceptions.ServiceException(str(serializer.errors))

    @classmethod
    def sync(
        cls,
        repo: models.Repository,
        remote_id: int,
        title: str,
        description: str,
        state: str,
        labels: t.List[str],
        url: str,
        created_at: datetime,
        updated_at: datetime,
        closed_at: datetime = None,
    ) -> t.Tuple[models.Issue, bool]:
        """
        Synchronizes issue by specified data.
        """
        validated_data = cls.validate(
            remote_id=remote_id,
            title=title,
            description=description,
            state=state,
            labels=labels,
            url=url,
            created_at=created_at,
            closed_at=closed_at,
            updated_at=updated_at,
        )

        remote_id = validated_data.pop("remote_id")

        issue, created = models.Issue.objects.update_or_create(
            repository=repo, remote_id=remote_id, defaults=validated_data,
        )

        return issue, created

    @staticmethod
    def delete_by_remote_id(repo: models.Repository, remote_id: str):
        """
        Finds and deletes repository issue by id.
        """
        models.Issue.objects.filter(repository=repo, remote_id=remote_id).delete()
