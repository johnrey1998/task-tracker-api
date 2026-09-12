from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.config import settings
from app.tasks.router import router as tasks_router
from app.users.router import router as users_router




def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0"
    )

    application.include_router(
        auth_router,
        prefix=f"{settings.api_prefix}/auth",
        tags=["auth"]
    )

    application.include_router(
        auth_router,
        prefix=f"{settings.api_prefix}/users",
        tags=["users"]
    )

    application.include_router(
        auth_router,
        prefix=f"{settings.api_prefix}/tasks",
        tags=["tasks"]
    )

    return application

app = create_app()
