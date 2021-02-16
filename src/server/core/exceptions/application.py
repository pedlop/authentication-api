from starlette.exceptions import HTTPException


class ApplicationException(HTTPException):
    def __init__(self, code: int, tip: str, message: str) -> None:
        self.code = code
        self.status_code = code
        self.tip = tip
        self.message = message
