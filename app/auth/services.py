from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest
from app.exceptions import InvalidCredentials
from app.security import create_token, verify_password
from app.users.services import get_user_by_email

def auth_user(session: Session, login_data: LoginRequest) -> str:
    user = get_user_by_email(session=session, email=str(login_data.email))

    if user is None or not verify_password(login_data.password, user.password_hash):
        raise InvalidCredentials("Invalid email or password")
    
    return create_token(user.id)
