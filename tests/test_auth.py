import pytest

from app.auth.schemas import LoginRequest
from app.auth.services import auth_user
from app.exceptions import InvalidCredentials
from app.security import decode_token
from app.users.schemas import UserCreate
from app.users.services import create_user

def test_auth_user_returns_token(database_session) -> None:
    create_user(database_session, UserCreate(
        name="John Doe",
        email="JOhNDoe@example.com",
        password="JaNe-DOE123",
        )
    )

    token = auth_user(
        database_session,
        LoginRequest(email="johndoe@example.com", password="JaNe-DOE123")
    )

    payload = decode_token(token)

    assert payload["sub"] == "1"
    assert "exp" in payload

def test_auth_user_rejects_unknown_email(database_session) -> None:
    login_data = LoginRequest(
        email="joey@random.com",
        password="joes-password"
    )

    with pytest.raises(InvalidCredentials, match="Invalid email or password"):
        auth_user(database_session, login_data)


def test_auth_user_rejects_incorrect_password(database_session) -> None:
    create_user(database_session, UserCreate(
        name="John Doe",
        email="JOhNDoe@example.com",
        password="JaNe-DOE123",
        )
    )

    login_data = LoginRequest(
        email="JOhNDoe@example.com",
        password="wrong-password"
    )

    with pytest.raises(InvalidCredentials, match="Invalid email or password"):
        auth_user(database_session, login_data)