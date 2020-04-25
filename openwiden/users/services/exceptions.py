class ServiceException(Exception):
    pass


class OAuthServiceException(ServiceException):
    pass


class ClientNotFound(OAuthServiceException):
    pass
