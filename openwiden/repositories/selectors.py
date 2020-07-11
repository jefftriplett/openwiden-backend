from django.db.models import QuerySet, Q

from openwiden import enums, exceptions
from openwiden.users.models import User

from . import models, error_messages


def get_added_and_public_repositories() -> "QuerySet[models.Repository]":
    query = Q(is_added=True, visibility=enums.VisibilityLevel.public)
    return models.Repository.objects.filter(query)


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
