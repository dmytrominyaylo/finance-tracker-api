class AppException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class ConflictException(AppException):
    pass


class NotFoundException(AppException):
    pass


class UnauthorizedException(AppException):
    pass
