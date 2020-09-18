from openwiden.exceptions import ServiceException

from . import messages


class RepositoryServiceException(ServiceException):
    app_id = 2


class RepositoryAlreadyAdded(RepositoryServiceException):
    error_message = messages.REPOSITORY_ALREADY_ADDED
    error_code = 1


class RepositoryCannotBeAddedDueToState(RepositoryServiceException):
    error_message = messages.REPOSITORY_CANNOT_BE_ADDED_DUE_TO_STATE
    error_code = 2


class RepositoryAlreadyRemoved(RepositoryServiceException):
    error_message = messages.REPOSITORY_ALREADY_REMOVED
    error_code = 3


class NotAddedRepositoryCannotBeRemoved(RepositoryServiceException):
    error_message = messages.NOT_ADDED_REPOSITORY_CANNOT_BE_REMOVED
    error_code = 4


class RepositoryDoesNotExist(RepositoryServiceException):
    error_message = messages.REPOSITORY_DOES_NOT_EXIST
    error_code = 5
