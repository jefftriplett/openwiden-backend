class ServiceException(Exception):
    def __init__(self, description: str, error=None):
        self.description = description
        self.error = error

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


class ProfileValidateException(OAuthServiceException):
    def __init__(self, error):
        description = (
            "An error occurred while creating the user. "
            "We apologize for the inconvenience, we will try to solve the problem as soon as possible."
        )
        super().__init__(description, error)


class ProviderNotImplemented(OAuthServiceException):
    def __init__(self, provider: str):
        super().__init__(f"{provider} is not implemented.")
