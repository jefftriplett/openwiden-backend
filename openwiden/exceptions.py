class ServiceException(Exception):
    def __init__(self, description: str, error=None):
        self.description = description
        self.error = error

    def __str__(self):
        return self.description
