from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.api.router import api_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, lifespan=lifespan)
    application.add_middleware(
        SessionMiddleware, secret_key=settings.session_secret_key
    )
    application.include_router(api_router, prefix="/api/v1")

    @application.get("/health")
    async def root_health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_application()
