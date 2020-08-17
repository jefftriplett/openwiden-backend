from typing import Set

from django.db.models import Func, QuerySet, Q

from openwiden import exceptions
from openwiden.users.models import User

from . import models, error_messages, enums


class HStoreSetKeys(Func):
    function = "skeys"


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


def get_programming_languages() -> Set[str]:
    """
    Returns set of the unique programming languages names from the all repositories.
    """
    return (
        models.Repository.objects.annotate(names=HStoreSetKeys("programming_languages"))
        .values_list("names", flat=True)
        .order_by("names")
        .distinct()
    )
