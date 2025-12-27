from typing import Annotated, Generator

from fastapi import Depends
from pydantic import EmailStr
from sqlmodel import Session, select

from backend.database.db import engine
from backend.database.models import UserModel

user: UserModel | None = None


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def current_user() -> UserModel:
    if not user:
        raise Exception("There is no current user")
    return user


def set_current_user(session: Session, email: EmailStr | str | None) -> None:
    global user
    if email:
        user = session.exec(
            select(UserModel).where(UserModel.email == email)
        ).first()
    else:
        user = None


SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[UserModel, Depends(current_user)]
