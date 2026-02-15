class AppErrorException(Exception):
    pass


class NotFoundException(AppErrorException):
    pass


class PermissionDeniedException(AppErrorException):
    pass

class EntityAlreadyExistsException(AppErrorException):
    pass

# The service layer is responsible for checking and handling
# known business exceptions, NOT DOMAIN!
