from starlette.exceptions import HTTPException


class ApplicationException(HTTPException):
    def __init__(self, code: int, reason: str, message: str) -> None:
        self.code = code
        self.status_code = code
        self.reason = reason
        self.message = message
