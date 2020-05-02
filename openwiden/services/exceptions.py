class ServiceException(Exception):
    """
    Base service exception for all subclasses.
    """

    def __init__(self, description: str, error=None):
        self.description = description
        self.error = error

    def __str__(self):
        return self.description
