from fastapi import APIRouter, HTTPException, status


from app.users.schemas import UserCreate, UserResponse
from app.deps import SessionDep
from app.exceptions import UserAlreadyExists
from app.users.services import create_user


router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
def register_user(user_data: UserCreate, session: SessionDep) -> UserResponse:
    try:
        return create_user(
            session=session,
            user_data=user_data,
        )

    except UserAlreadyExists as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        ) from error

