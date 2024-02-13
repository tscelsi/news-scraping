class RepositoryException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message


class RepositoryInvalidIdError(RepositoryException):
    pass


class ObjectNotFoundError(RepositoryException):
    pass
