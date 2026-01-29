from typing import Annotated, Generator

from fastapi import Depends
from pydantic import EmailStr
from sqlmodel import Session, select

from backend.database.init_db import engine
from backend.database.models import UserModel

user: UserModel = UserModel()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def current_user() -> UserModel:
    return user


def set_current_user(session: Session, email: EmailStr | str | None) -> None:
    global user
    if email:
        user = session.exec(
            select(UserModel).where(UserModel.email == email)
        ).one()
    else:
        user = UserModel()


SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[UserModel, Depends(current_user)]
