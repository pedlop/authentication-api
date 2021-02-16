from server.database import users_collection


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
    user = await users_collection.insert_one(user_data)
    new_user = await users_collection.find_one({"_id": user.inserted_id})
    return auth_user_helper(new_user)


async def retrieve_auth_user(username: str, pass_on=False) -> dict:
    print(username)
    user = await users_collection.find_one({"username": username})
    if user:
        return auth_user_helper(user, pass_on)