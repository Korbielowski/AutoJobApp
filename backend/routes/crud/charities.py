from backend.database.crud import get_charities, delete_model, save_model
from backend.database.models import CharityModel
from backend.schemas.endpoints import CharityPost, Charity
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="charities")


@router.get("/")
async def read_charities(user: CurrentUser, session: SessionDep):
    return get_charities(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_charity(user: CurrentUser, session: SessionDep):
    return get_charities(session, user, use_base_model=True)


@router.post("/")
async def create_charity(
        user: CurrentUser, session: SessionDep, item: Charity
):
    save_model(session, user, CharityModel.model_validate(item))


@router.put("/{item_id}")
async def update_charity(
        user: CurrentUser, session: SessionDep, item_id: int, item: CharityPost
):
    model_to_update = session.exec(
        select(CharityModel).where(CharityModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_charity(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, CharityModel, item_id)
