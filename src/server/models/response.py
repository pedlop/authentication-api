def ResponseModel(data, message=None):
    return {"data": data, "code": 200, "message": message}


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}