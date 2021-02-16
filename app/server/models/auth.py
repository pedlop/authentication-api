from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str
    token_expires: float


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenClient(BaseModel):
    is_logged: bool
    expires_in: int


class AuthUserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = False

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
                "disabled": False,
            }
        }