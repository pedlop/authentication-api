from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class Token(BaseModel):
    access_token: str
    token_type: str
    token_expires: float


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenClient(BaseModel):
    is_logged: bool
    expires_in: int
    user_id: str
    user_role: RoleEnum


class TokenJwt(BaseModel):
    sub: str
    uid: str
    role: RoleEnum


def TokenJwtModel(username: str, id: str, role: RoleEnum) -> TokenJwt:
    return {"sub": username, "uid": id, "role": role}


def TokenClientModel(
    is_logged: bool,
    expires_in: datetime = None,
    user_id: str = None,
    user_role: RoleEnum = None,
) -> TokenClient:
    return {
        "is_logged": is_logged,
        "expires_in": expires_in,
        "user_id": user_id,
        "user_role": user_role,
    }


class AuthUserSchema(BaseModel):
    username: str = Field(...)
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    role: Optional[RoleEnum] = RoleEnum.USER
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        schema_extra = {
            "example": {
                "username": "joe",
                "password": "12345",
                "email": "jdoe@x.edu.ng",
                "full_name": "John Doe",
            }
        }


class ReadAuthUserModel(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "joe",
                "email": "jdoe@x.edu.ng",
                "full_name": "John Doe",
                "created_at": "2021-01-17T12:00:00.387+00:00",
                "updated_at": "2021-01-17T12:00:00.387+00:00",
            }
        }


class UpdateAuthUserModel(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    full_name: Optional[str]
    disabled: Optional[bool]
    updated_at: datetime = datetime.now()

    class Config:
        schema_extra = {
            "example": {
                "username": "joe",
                "email": "jdoe@x.edu.ng",
                "full_name": "John Doe",
            }
        }


class AuthResetPasswordModel(BaseModel):
    token: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "password": "54321",
            }
        }