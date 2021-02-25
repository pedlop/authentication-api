from datetime import datetime
from src.server.models.auth import ReadAuthUserModel
from typing import List
from bson.objectid import ObjectId
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
        "role": user["role"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }
    if pass_on:
        data["password"] = user["password"]
        # data["role"] = user["role"]
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


async def update_auth_user(id: str, data: dict) -> bool:
    if len(data) < 1:
        return False
    user = await users_collection.find_one({"_id": ObjectId(id)})
    if user:
        data["updated_at"] = datetime.now()
        updated_user = await users_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_user:
            return True
        return False


async def retrieve_all_users() -> List[ReadAuthUserModel]:
    try:
        # print(documents)
        users = []
        async for doc in users_collection.find():
            users.append(auth_user_helper(doc))
        print(users)
        return users
    except Exception as e:
        print(e)