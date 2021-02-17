from fastapi import status

from pymongo import errors as MongoErrors

from src.server.database import users_collection
from src.server.core.exceptions.application import ApplicationException


def auth_user_helper(user, pass_on=False) -> dict:
    data = {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "disabled": user["disabled"],
    }
    if pass_on:
        data["password"] = user["password"]
    return data


async def add_auth_user(user_data: dict) -> dict:
    try:
        user = await users_collection.insert_one(user_data)
        new_user = await users_collection.find_one({"_id": user.inserted_id})
        return auth_user_helper(new_user)
    except MongoErrors.DuplicateKeyError as e:
        reason = e.details.get("keyValue")
        key = next(iter(reason))
        value = reason.get(key)
        raise ApplicationException(
            status.HTTP_400_BAD_REQUEST,
            f"The {key} '{value}' already exists",
            str(e),
        )
    except Exception as e:
        raise ApplicationException(
            status.HTTP_400_BAD_REQUEST, "User can not be saved", str(e)
        )


async def retrieve_auth_user(username: str, pass_on=False) -> dict:
    try:
        user = await users_collection.find_one({"username": username})
        if user:
            return auth_user_helper(user, pass_on)
    except Exception as e:
        raise ApplicationException(status.HTTP_404_NOT_FOUND, "User not found", str(e))
