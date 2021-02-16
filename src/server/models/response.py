def ResponseModel(data, success: str = None, warning: str = None):
    return {"data": data, "success_message": success, "warning_message": warning}


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}