from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import UserAlreadyExists
from app.security import hash_password
from app.users.models import User
from app.users.schemas import UserCreate

def create_user(session: Session, user_data: UserCreate) -> User:
    user = User(
        name=user_data.name,
        email=str(user_data.email).lower(),
        password_hash=hash_password(user_data.password),
    )

    session.add(user)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise UserAlreadyExists(
            "A user with this email already exists"
        ) from error

    session.refresh(user)
    return user

# used for authentication logic
def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email.lower(),)

    return session.scalar(statement)

# used relational logic
def get_user_by_id(session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)

    return session.scalar(statement)