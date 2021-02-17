def object_to_mongo_dict(data: object) -> dict:
    return {k: v for k, v in data.dict().items() if v is not None}