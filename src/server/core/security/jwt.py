from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from decouple import config
from starlette.requests import Request

from src.server.core.exceptions.application import ApplicationException
from src.server.models.auth import ReadAuthUserModel, RoleEnum, Token, TokenData
from src.server.services.auth import retrieve_auth_user

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def read_user_from_token(
    access_token: str, permission: RoleEnum = None
) -> ReadAuthUserModel:
    if access_token:
        user = await user_token_data(access_token)
        if user and user["disabled"] is False:
            del user["disabled"]
            if permission == None:
                return user
            elif user["role"] == permission:
                return user
        else:
            raise ApplicationException(
                status.HTTP_400_BAD_REQUEST,
                "Inactive user",
                "This user has been disabled or does not exist",
            )
    raise ApplicationException(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid credentials",
        "Could not validate credentials - invalid token, cookie or permission",
    )


async def user_token_data(access_token: str) -> ReadAuthUserModel:
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username:
            token_data = TokenData(username=username)
            if token_data:
                return await retrieve_auth_user(token_data.username)
        return None
    except JWTError:
        return None
