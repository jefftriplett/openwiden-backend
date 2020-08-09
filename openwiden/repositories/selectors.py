from django.db.models import QuerySet, Q

from openwiden import exceptions
from openwiden.users.models import User

from . import models, error_messages, enums


def get_added_repositories() -> "QuerySet[models.Repository]":
    return models.Repository.objects.filter(state=enums.RepositoryState.ADDED)


def get_repository(*, id: str) -> models.Repository:
    try:
        return models.Repository.objects.get(id=id)
    except models.Repository.DoesNotExist:
        error = error_messages.REPOSITORY_DOES_NOT_EXIST.format(id=id)
        raise exceptions.ServiceException(error)


def get_user_repositories(*, user: User) -> "QuerySet[models.Repository]":
    """
    Returns user's repos filters by owner or organization membership.
    """
    query = Q(owner__user=user) | Q(organization__member__vcs_account__user=user)
    return models.Repository.objects.filter(query)
