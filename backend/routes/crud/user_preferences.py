from backend.database.crud import get_user_preferences, delete_model, save_model
from backend.database.models import UserPreferencesModel
from backend.schemas.endpoints import UserPreferencesPost
from backend.schemas.models import UserPreferences
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="/user_preferences")


@router.get("/")
async def read_user_preferences(user: CurrentUser, session: SessionDep):
    return get_user_preferences(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_user_preferences(user: CurrentUser, session: SessionDep):
    return get_user_preferences(session, user, use_base_model=True)


@router.post("/")
async def create_user_preferences(
        user: CurrentUser, session: SessionDep, item: UserPreferences
):
    save_model(session, user, UserPreferencesModel.model_validate(item))


@router.put("/{item_id}")
async def update_user_preferences(
        user: CurrentUser, session: SessionDep, item_id: int, item: UserPreferencesPost
):
    model_to_update = session.exec(
        select(UserPreferencesModel).where(UserPreferencesModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_user_preferences(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, UserPreferencesModel, item_id)
