from datetime import datetime, timedelta
from typing import Optional
import locale

locale.setlocale(locale.LC_ALL, "pt_BR")

from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
    Body,
    Cookie,
    Depends,
)
from fastapi.security import OAuth2PasswordRequestForm


from src.server.core.security.jwt import (
    create_access_token,
    read_user_from_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.server.core.security.bcrypt import hash_encrypted_text, verify_encrypted_text
from src.server.core.security.cookie import set_cookie
from src.server.core.exceptions.application import ApplicationException
from src.server.models.response import ApplicationResponse, ResponseModel
from src.server.models.auth import (
    TokenClient,
    ReadAuthUserModel,
    AuthUserSchema,
    AuthResetPasswordModel,
    UpdateAuthUserModel,
    TokenClientModel,
    TokenJwtModel,
)
from src.server.services.auth import (
    add_auth_user,
    retrieve_all_users,
    retrieve_auth_user,
    update_auth_user,
)
from src.server.core.utils.utils import object_to_mongo_dict


router = APIRouter()


def token_cookie_handler(
    user: ReadAuthUserModel, response: Response
) -> ApplicationResponse[TokenClient]:
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = TokenJwtModel(user["username"], user["id"], user["role"])
    access_token = create_access_token(data=token_data, expires_delta=token_expires)
    expires_in = (datetime.now() + token_expires).isoformat()
    token = {
        "token_type": "bearer",
        "access_token": access_token,
        "token_expires": expires_in,
    }
    set_cookie(response, token, ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenClientModel(True, user["id"], expires_in, user["role"])


@router.post("/signup", response_description="User registered into database")
async def signup(body: AuthUserSchema = Body(...)):
    user = object_to_mongo_dict(body)
    user["password"] = hash_encrypted_text(user["password"])
    new_user = await add_auth_user(user)
    return ResponseModel(new_user, "Auth user added successfully.")


@router.post("/signin")
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    response: Response = None,
) -> ApplicationResponse[TokenClient]:
    user = await retrieve_auth_user(form_data.username, True)
    exception = ApplicationException(
        status.HTTP_401_UNAUTHORIZED,
        "Incorrect username or password",
        "Could not validate credentials",
    )
    if not user:
        raise exception
    if not verify_encrypted_text(form_data.password, user["password"]):
        raise exception
    data = token_cookie_handler(user, response)
    return ResponseModel(data, f'Welcome {user["username"]}!')


@router.patch("/signout")
async def signout(
    request: Request = None, response: Response = None
) -> ApplicationResponse[TokenClient]:
    token = {
        "token_type": "",
        "access_token": "",
        "token_expires": "",
    }
    set_cookie(response, token, 0)
    data = TokenClientModel(False)
    return ResponseModel(data, "See you later!")


@router.get("/check")
async def check_user_authenticate_status(
    request: Request = None,
    pedlop_oauth_token_type: Optional[str] = Cookie(None),
    pedlop_oauth_access_token: Optional[str] = Cookie(None),
    pedlop_oauth_token_expires: Optional[str] = Cookie(None),
) -> ApplicationResponse[TokenClient]:
    print("Req", request.cookies)
    print("TOKEN", pedlop_oauth_access_token)
    data = TokenClientModel(False)
    if (
        pedlop_oauth_token_type
        and pedlop_oauth_access_token
        and pedlop_oauth_token_expires
    ):
        user = await read_user_from_token(pedlop_oauth_access_token)
        if user:
            data = TokenClientModel(
                True, user["id"], pedlop_oauth_token_expires, user["role"]
            )
    return ResponseModel(data)


@router.patch("/refresh")
async def refresh_access_token(
    pedlop_oauth_access_token: Optional[str] = Cookie(None), response: Response = None
):
    user = await read_user_from_token(pedlop_oauth_access_token)
    data = token_cookie_handler(user, response)
    return ResponseModel(data)


@router.get("/profile")
async def read_users_me(pedlop_oauth_access_token: Optional[str] = Cookie(None)):
    data = await read_user_from_token(pedlop_oauth_access_token)
    return ResponseModel(data)


@router.put("/profile")
async def update_profile(
    pedlop_oauth_access_token: Optional[str] = Cookie(None),
    body: UpdateAuthUserModel = Body(...),
) -> ApplicationResponse[None]:
    user = await read_user_from_token(pedlop_oauth_access_token)
    req = object_to_mongo_dict(body)
    password = req.get("password")
    if password:
        req["password"] = hash_encrypted_text(password)
    updated_user = await update_auth_user(user["id"], req)
    if updated_user:
        return ResponseModel(None, "Auth user has been successfully updated")
    else:
        raise ApplicationException(
            status.HTTP_400_BAD_REQUEST, "Error when resetting password"
        )


@router.put("/reset-password")
async def reset_password(
    body: AuthResetPasswordModel = Body(...),
) -> ApplicationResponse[None]:
    user = await read_user_from_token(body.token)
    new_password = hash_encrypted_text(body.password)
    updated_user = await update_auth_user(user["id"], {"password": new_password})
    if updated_user:
        return ResponseModel(None, "Password reset successfully")
    else:
        raise ApplicationException(
            status.HTTP_400_BAD_REQUEST, "Error when resetting password"
        )


@router.get("/users")
async def read_users(pedlop_oauth_access_token: Optional[str] = Cookie(None)):
    await read_user_from_token(pedlop_oauth_access_token, permission="ADMIN")
    users = await retrieve_all_users()
    return ResponseModel(users)


@router.put("/users/{id}")
async def read_users(
    id: str,
    body: UpdateAuthUserModel = Body(...),
    pedlop_oauth_access_token: Optional[str] = Cookie(None),
):
    await read_user_from_token(pedlop_oauth_access_token, permission="ADMIN")
    req = object_to_mongo_dict(body)
    updated_user = await update_auth_user(id, req)
    print(updated_user)
    if updated_user:
        return ResponseModel(None, "Auth user has been successfully updated")
    else:
        raise ApplicationException(
            status.HTTP_400_BAD_REQUEST, "Error when updating user"
        )