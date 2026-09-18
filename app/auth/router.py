from fastapi import APIRouter, HTTPException, status
from app.auth.schemas import TokenResponse, LoginRequest
from app.auth.services import auth_user
from app.deps import SessionDep
from app.exceptions import InvalidCredentials


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, session: SessionDep) -> TokenResponse:
    try:
        token = auth_user(session=session, login_data=login_data)
    except InvalidCredentials as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    return TokenResponse(access_token=token)