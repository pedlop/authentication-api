from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from decouple import config
from starlette.requests import Request

from src.server.core.exceptions.application import ApplicationException
from src.server.models.auth import ReadAuthUserModel, Token, TokenData
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


async def read_user_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = ApplicationException(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid credentials",
        "Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await retrieve_auth_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def read_user_token_from_cookie(access_token: str):
    if access_token:
        user = await user_token_data(access_token)
        if user:
            return user
    raise ApplicationException(
        status.HTTP_401_UNAUTHORIZED,
        "Invalid credentials",
        "Could not validate credentials - invalid token or cookie",
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
