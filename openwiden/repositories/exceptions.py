from openwiden.exceptions import ServiceException

from . import messages, apps


class RepositoryException(ServiceException):
    app_id = apps.RepositoriesConfig.unique_id


class RepositoryAlreadyAdded(RepositoryException):
    error_message = messages.REPOSITORY_ALREADY_ADDED
    error_code = 1


class RepositoryCannotBeAddedDueToState(RepositoryException):
    error_message = messages.REPOSITORY_CANNOT_BE_ADDED_DUE_TO_STATE
    error_code = 2


class RepositoryAlreadyRemoved(RepositoryException):
    error_message = messages.REPOSITORY_ALREADY_REMOVED
    error_code = 3


class NotAddedRepositoryCannotBeRemoved(RepositoryException):
    error_message = messages.NOT_ADDED_REPOSITORY_CANNOT_BE_REMOVED
    error_code = 4


class RepositoryDoesNotExist(RepositoryException):
    error_message = messages.REPOSITORY_DOES_NOT_EXIST
    error_code = 5
