from fastapi import Response
from decouple import config

from server.models.auth import Token


def set_cookie(response: Response, token: Token, expires_in):
    is_production = config("ENV") == "production"
    print(is_production, token)
    for key in token:
        print(key)
        response.set_cookie(
            key=key, value=token[key], expires=expires_in, secure=is_production
        )
