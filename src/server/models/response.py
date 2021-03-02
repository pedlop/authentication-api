from typing import TypeVar, Generic

T = TypeVar("T")


class ApplicationResponse(Generic[T]):
    data: T
    success_message: str
    warning_message: str


def ResponseModel(data, success: str = None, warning: str = None):
    return {"data": data, "success_message": success, "warning_message": warning}


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}