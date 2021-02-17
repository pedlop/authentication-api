from fastapi import Response
from decouple import config

from src.server.models.auth import Token
from src.server.models.config import Config


def set_cookie(response: Response, token: Token, expires_in: float):
    is_production = config("ENV") == "production"
    for key in token:
        credential_key = f"{Config.COOKIE_PREFIX.value}{key}"
        response.set_cookie(
            key=credential_key,
            value=token[key],
            expires=expires_in,
            secure=is_production,
        )
