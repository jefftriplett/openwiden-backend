from typing import Set

from django.db.models import Func, QuerySet, Q

from openwiden.users.models import User

from . import models, enums, exceptions


class HStoreSetKeys(Func):
    function = "skeys"


def get_added_repositories() -> "QuerySet[models.Repository]":
    return models.Repository.objects.filter(state=enums.RepositoryState.ADDED).select_related("owner", "organization")


def get_repository(*, id: str) -> models.Repository:
    try:
        return models.Repository.objects.get(id=id)
    except models.Repository.DoesNotExist:
        raise exceptions.RepositoryDoesNotExist(id=id)


def get_user_repositories(*, user: User) -> "QuerySet[models.Repository]":
    """
    Returns user's repos filters by owner or organization membership.
    """
    query = Q(owner__user=user) | Q(organization__member__vcs_account__user=user)
    return models.Repository.objects.filter(query).select_related("owner", "organization")


def get_programming_languages() -> Set[str]:
    """
    Returns set of the unique programming languages names from the all added repositories.
    """
    return (
        models.Repository.objects.filter(state=enums.RepositoryState.ADDED)
        .annotate(names=HStoreSetKeys("programming_languages"))
        .order_by("names")
        .distinct()
        .values_list("names", flat=True)
    )
