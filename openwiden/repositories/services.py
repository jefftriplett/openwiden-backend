import typing as t
from datetime import datetime

from django.db.models import QuerySet

from openwiden import enums, exceptions
from openwiden.repositories import models, error_messages
from openwiden.users import models as users_models, selectors as users_selectors
from openwiden.organizations import models as organizations_models
from openwiden.webhooks import services as webhooks_services


TaskID = str


class Repository:
    @staticmethod
    def sync(
        vcs: str,
        remote_id: int,
        name: str,
        url: str,
        created_at: datetime,
        updated_at: datetime,
        description: str = None,
        owner: users_models.User = None,
        organization: organizations_models.Organization = None,
        stars_count: int = 0,
        open_issues_count: int = 0,
        forks_count: int = 0,
        programming_languages: dict = None,
        visibility: str = enums.VisibilityLevel.private,
    ) -> t.Tuple[models.Repository, bool]:
        """
        Synchronizes repository with specified data (update or create).
        """
        fields = dict(
            name=name,
            url=url,
            description=description,
            owner=owner,
            organization=organization,
            stars_count=stars_count,
            open_issues_count=open_issues_count,
            forks_count=forks_count,
            programming_languages=programming_languages,
            visibility=visibility,
            created_at=created_at,
            updated_at=updated_at,
        )

        # Try to create or update repository
        try:
            repository = models.Repository.objects.get(vcs=vcs, remote_id=remote_id)
        except models.Repository.DoesNotExist:
            repository = models.Repository.objects.create(vcs=vcs, remote_id=remote_id, is_added=False, **fields,)
            created = True
        else:
            # Update values if repository exist
            for k, v in fields.items():
                setattr(repository, k, v)
            repository.save(update_fields=fields.keys())
            created = False

        # TODO: notify
        if created:
            pass

        return repository, created

    @staticmethod
    def added(visibility: str = enums.VisibilityLevel.public) -> QuerySet:
        """
        Returns repositories QuerySet filtered by "is_added" field and optional visibility (default is public).
        """
        return models.Repository.objects.filter(is_added=True, visibility=visibility)

    @classmethod
    def get_added_and_public_(cls) -> QuerySet:
        """
        Returns added and public visible repositories also known as "OpenWiden".
        """
        return cls.added(enums.VisibilityLevel.public)


def sync_issue(
    *,
    repository: models.Repository,
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
    issue, created = models.Issue.objects.update_or_create(
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
            closed_at=closed_at,
        ),
    )

    return issue, created


def delete_by_remote_id(*, remote_id: str):
    """
    Finds and deletes repository issue by id.
    """
    models.Issue.objects.filter(remote_id=remote_id).delete()


def add_repository(*, repository: models.Repository, user: users_models.User) -> None:
    """
    Adds existed repository by sync related objects (issues, for example) and changes
    status to "is_added".
    """
    vcs_account = users_selectors.find_vcs_account(user, repository.vcs)

    # Check if repository is already added and raise an error if yes
    if repository.is_added:
        raise exceptions.ServiceException(error_messages.REPOSITORY_ALREADY_ADDED)
    elif repository.visibility == enums.VisibilityLevel.private:
        raise exceptions.ServiceException(error_messages.REPOSITORY_IS_PRIVATE_AND_CANNOT_BE_ADDED)

    # Set is_added True for now, but save in sync action (if success)
    repository.is_added = True

    # Call repository sync action
    webhooks_services.create_github_repository_webhook(
        repository=repository, vcs_account=vcs_account,
    )

    repository.save(update_fields=("is_added",))
