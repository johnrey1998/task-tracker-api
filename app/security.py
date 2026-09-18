from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from pwdlib import PasswordHash

from app.config import settings

from app.exceptions import InvalidAccessToken

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_token(subject: str | int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.token_expiration_hours)

    payload = {
        "sub": str(subject),
        "exp": expires_at,
    }


    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )

def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]}
        )
    except jwt.ExpiredSignatureError as error:
        raise InvalidAccessToken("Access token has expired") from error
    except jwt.InvalidTokenError as error:
        raise InvalidAccessToken("Invalid access token") from error
    
    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject:
        raise InvalidAccessToken("Access token has an invalid subject")
    
    return payload


