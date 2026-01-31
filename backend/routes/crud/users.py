from backend.database.crud import get_users, delete_user, save_model
from backend.database.models import LocationModel
from backend.schemas.endpoints import LocationPost, Location
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="users")


@router.get("/")
async def read_users(user: CurrentUser, session: SessionDep):
    return get_users(session)


@router.get("/{item_id}")
async def read_user(user: CurrentUser, session: SessionDep):
    return get_users(session)


@router.post("/")
async def create_user(
        user: CurrentUser, session: SessionDep, item: Location
):
    save_model(session, user, LocationModel.model_validate(item))


@router.put("/{item_id}")
async def update_user(
        user: CurrentUser, session: SessionDep, item_id: int, item: LocationPost
):
    model_to_update = session.exec(
        select(LocationModel).where(LocationModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_userx(user: CurrentUser, session: SessionDep, item_id: int):
    delete_user(session, user.email)
