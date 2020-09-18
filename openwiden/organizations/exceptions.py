from openwiden.exceptions import ServiceException

from . import messages, apps


class OrganizationException(ServiceException):
    app_id = apps.OrganizationsAppConfig.unique_id


class UserIsNotOrganizationMember(OrganizationException):
    error_code = 1
    error_message = messages.USER_IS_NOT_ORGANIZATION_MEMBER
