from backend.database.crud import get_locations, delete_model, save_model
from backend.database.models import LocationModel
from backend.schemas.endpoints import LocationPost, Location
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="locations")


@router.get("/")
async def read_locations(user: CurrentUser, session: SessionDep):
    return get_locations(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_location(user: CurrentUser, session: SessionDep):
    return get_locations(session, user, use_base_model=True)


@router.post("/")
async def create_location(
    user: CurrentUser, session: SessionDep, item: Location
):
    save_model(session, user, LocationModel.model_validate(item))


@router.put("/{item_id}")
async def update_location(
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
async def delete_location(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, LocationModel, item_id)
