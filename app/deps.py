from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_database
from app.exceptions import InvalidAccessToken
from app.security import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SessionDep = Annotated[Session, Depends(get_database)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

def get_current_user_id(token: TokenDep) -> int:
    try:
        payload = decode_token(token)
        subject = payload["sub"]
        return int(subject)
    except (InvalidAccessToken, KeyError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error



