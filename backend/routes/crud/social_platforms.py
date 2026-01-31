from backend.database.crud import get_locations, delete_model, save_model
from backend.database.models import SocialPlatformModel
from backend.schemas.endpoints import SocialPlatformPost, SocialPlatform
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="social-platforms")


@router.get("/")
async def read_social_platforms(user: CurrentUser, session: SessionDep):
    return get_locations(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_social_platform(user: CurrentUser, session: SessionDep):
    return get_locations(session, user, use_base_model=True)


@router.post("/")
async def create_social_platforms(
        user: CurrentUser, session: SessionDep, item: SocialPlatform
):
    save_model(session, user, SocialPlatformModel.model_validate(item))


@router.put("/{item_id}")
async def update_social_platform(
        user: CurrentUser, session: SessionDep, item_id: int, item: SocialPlatformPost
):
    model_to_update = session.exec(
        select(SocialPlatformModel).where(SocialPlatformModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_social_platform(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, SocialPlatformModel, item_id)
