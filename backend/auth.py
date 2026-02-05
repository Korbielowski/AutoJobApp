from sqlmodel import func
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request
from starlette.types import Receive, Scope, Send

from backend.config import settings
from backend.database.models import UserModel
from backend.routes.deps import current_user, get_session
from backend.logger import get_logger

logger = get_logger()

async def _verify_user(request: Request) -> str | None:
    session = next(get_session())
    user_count = session.scalar(func.count(UserModel.id))

    if not current_user().email and user_count >= 1:
        return  "login.html"
    elif user_count == 0:
        return "register.html"
    return None



class AuthStaticFiles(StaticFiles):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive)
        url_path = request.url.path
        file_name = None

        if "login" not in url_path and "register" not in url_path:
            file_name = await _verify_user(request)
            logger.info(f"{type(file_name)}, {file_name}")

        if file_name:
            response = FileResponse(path=settings.STATIC_PATH / file_name, status_code=303)
            logger.debug(f"Redirecting from {request.url.path} to {response.path}")
            await response(scope, receive, send)
        else:
            await super().__call__(scope, receive, send)


