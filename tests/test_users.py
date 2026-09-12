import pytest

from app.exceptions import UserAlreadyExists
from app.security import verify_password
from app.users.schemas import UserCreate
from app.users.services import (
    create_user, get_user_by_email, get_user_by_id
)

def test_create_user(database_session) -> None:
    user_data = UserCreate(
        name="John Doe",
        email="JOhNDoe@example.com",
        password="JaNe-DOE123",
    )

    user = create_user(database_session, user_data)

    assert user.id is not None
    assert user.name == "John Doe"
    assert user.email == "johndoe@example.com"
    assert verify_password("JaNe-DOE123", user.password_hash)

def test_get_user_by_email(database_session) -> None:
    user = create_user(database_session, UserCreate(
        name="John Doe",
        email="JOhNDoe@example.com",
        password="JaNe-DOE123",
        )
    )

    result = get_user_by_email(database_session, "JOhNdoe@eXaMPle.cOm")

    assert result is not None
    assert result.id == user.id

def test_get_user_by_id(database_session) -> None:
    user = create_user(database_session, UserCreate(
        name="John Doe",
        email="JOhNDoe@example.com",
        password="JaNe-DOE123",
        )
    )

    result = get_user_by_id(database_session, user.id)

    assert result is not None
    assert result.email == user.email

def test_duplicate_email_raises_error(database_session) -> None:
    user_data = UserCreate(
        name="John Doe",
        email="JOhNDoe@example.com",
        password="JaNe-DOE123",
    )

    create_user(database_session, user_data)

    with pytest.raises(UserAlreadyExists):
        create_user(database_session, user_data)
    

