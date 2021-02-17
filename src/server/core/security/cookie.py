from datetime import datetime
from fastapi import Response
from fastapi.logger import logger
from decouple import config

from src.server.models.auth import Token
from src.server.models.config import Config


def set_cookie(response: Response, token: Token, max_age: float):
    # expires = datetime.now().microsecond
    # print(expires, max_age)
    is_production = config("ENV") == "production"
    domain = config("DOMAIN")
    for key in token:
        credential_key = f"{Config.COOKIE_PREFIX.value}{key}"
        response.set_cookie(
            key=credential_key,
            value=token[key],
            max_age=max_age,
            secure=is_production,
            domain=domain,
            httponly=True,
        )
