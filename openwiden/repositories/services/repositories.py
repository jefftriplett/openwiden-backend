import typing as t
from django.utils.translation import gettext_lazy as _
from django.db import models as m
from openwiden.repositories import models, enums


class Repository:
    @staticmethod
    def all() -> m.QuerySet:
        """
        Returns all repositories QuerySet.
        """
        return models.Repository.objects.all()

    @staticmethod
    def is_available_to_add(repository: models.Repository) -> t.Tuple[bool, t.Optional[str]]:
        """
        Returns repository status and message, that describes why it's not (if it is).
        """
        if repository.is_added is False:
            if repository.visibility == enums.VisibilityLevel.public:
                return True, None
            else:
                return False, _("{visibility} should be public.").format(visibility=repository.visibility)
        else:
            return False, _("{repository} already added.").format(repository=repository)

    @staticmethod
    def added(visibility: str = enums.VisibilityLevel.public) -> m.QuerySet:
        """
        Returns filtered by "is_added" field repositories QuerySet.
        """
        return models.Repository.objects.filter(is_added=True, visibility=visibility)

    @staticmethod
    def add(repository: models.Repository):
        """
        Adds the specified repository explicitly.
        """
        pass

    @staticmethod
    def delete(repository: models.Repository):
        """
        Soft deletes the specified repository.
        """
        pass
