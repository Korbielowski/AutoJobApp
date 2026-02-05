from sqlmodel import func
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request

from backend.config import settings
from backend.database.models import UserModel
from backend.routes.deps import current_user, get_session
from backend.logger import get_logger

logger = get_logger()

async def _verify_user(request: Request) -> FileResponse | None:
    session = get_session()
    user_count = session.scalar(func.count(UserModel.id))

    if not current_user().email and user_count >= 1:
        logger.debug(f"Redirecting from {request.url.path} to {settings.STATIC_PATH / 'login'}")
        return FileResponse(settings.STATIC_PATH / "login.html")
    elif user_count == 0:
        logger.debug(f"Redirecting from {request.url.path} to {settings.STATIC_PATH / 'register'}")
        return FileResponse(settings.STATIC_PATH / "register.html")
    return None



class AuthStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        request = Request(scope, receive)
        path =request.url.path
        if "login" not in path and "register" not in path:
            await _verify_user(request)
        await super().__call__(scope, receive, send)


