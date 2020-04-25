class ServiceException(Exception):
    def __init__(self, description: str):
        self.description = description

    def __str__(self):
        return self.description


class OAuthServiceException(ServiceException):
    pass


class ProviderNotFound(OAuthServiceException):
    def __init__(self, provider: str):
        super().__init__(f"client for {provider} is not found.")


class TokenFetchException(OAuthServiceException):
    pass


class ProfileRetrieveException(OAuthServiceException):
    pass


class ProviderNotImplemented(OAuthServiceException):
    def __init__(self, provider: str):
        super().__init__(f"{provider} is not implemented.")
