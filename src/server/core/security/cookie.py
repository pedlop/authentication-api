from datetime import datetime
from fastapi import Response
from decouple import config

from src.server.models.auth import Token
from src.server.models.config import Config


def set_cookie(response: Response, token: Token, minutes: int):
    is_production = config("ENV") == "production"
    domain = config("DOMAIN")
    max_age = minutes * 60
    samesite = "none" if is_production else "lax"
    print(is_production, domain)
    for key in token:
        credential_key = f"{Config.COOKIE_PREFIX.value}{key}"
        response.set_cookie(
            key=credential_key,
            value=token[key],
            max_age=max_age,
            domain=domain,
            httponly=True,
            samesite=samesite,
            secure=is_production,
        )
