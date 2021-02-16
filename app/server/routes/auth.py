from datetime import datetime, timedelta
from typing import Optional

from fastapi import (
    APIRouter,
    Body,
    Request,
    Response,
    Cookie,
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm


from server.core.security.jwt import (
    create_access_token,
    read_user_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from server.core.security.bcrypt import hash_encrypted_text, verify_encrypted_text
from server.core.security.cookie import set_cookie
from server.core.exceptions.application import ApplicationException
from server.models.response import ErrorResponseModel, ResponseModel
from server.models.auth import (
    Token,
    TokenData,
    TokenClient,
    AuthUserSchema,
    ReadAuthUserModel,
)
from server.services.auth import add_auth_user, retrieve_auth_user


router = APIRouter()


async def get_current_active_user(
    current_user: ReadAuthUserModel = Depends(read_user_token),
):
    if current_user["disabled"]:
        raise ApplicationException(
            status.HTTP_400_BAD_REQUEST, "Inactive user", "This user was disabled"
        )
    return current_user


@router.post("/signup", response_description="User registered into database")
async def signup(user: AuthUserSchema = Body(...)):
    user = jsonable_encoder(user)
    user["password"] = hash_encrypted_text(user["password"])
    new_user = await add_auth_user(user)
    return ResponseModel(new_user, "Auth user added successfully.")


@router.post("/signin")
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    response: Response = None,
):
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )

    token = {
        "token_type": "bearer",
        "access_token": access_token,
        "token_expires": access_token_expires,
    }

    client_host = request.client.host
    print(client_host)
    set_cookie(response, token, access_token_expires)

    data = {"is_logged": True, "expires_in": access_token_expires}
    return ResponseModel({**token, **data}, f'Welcome {user["username"]}!')


@router.get("/profile", response_model=ReadAuthUserModel)
async def read_users_me(
    current_user: ReadAuthUserModel = Depends(get_current_active_user),
):
    return current_user


@router.get("/check")
async def check_user_authenticate_status(
    token_type: Optional[str] = Cookie(None),
    access_token: Optional[str] = Cookie(None),
    token_expires: Optional[str] = Cookie(None),
):
    data = {"is_logged": False, "expires_in": 0}
    if token_type and access_token and token_expires:
        token = f"{token_type} {access_token}"
        print(token)
        user = await read_user_token(access_token)
        print(user)
        if user:
            # expires_in = (
            #     datetime.strptime(token_expires, "%H:%M:%S").timestamp().second()
            # )
            # print(expires_in)
            data = {"is_logged": True, "expires_in": token_expires}
    return ResponseModel(data)


@router.patch("/signout")
async def signout(response: Response = None):
    token = {
        "token_type": "",
        "access_token": "",
        "token_expires": "",
    }

    set_cookie(response, token, 0)
    data = {"is_logged": False, "expires_in": 0}
    return ResponseModel(data, "See you later!")
