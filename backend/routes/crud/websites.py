from backend.database.crud import get_websites, delete_model, save_model
from backend.database.models import WebsiteModel
from backend.schemas.endpoints import WebsitePost, Website
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="/websites")


@router.get("/")
async def read_websites(user: CurrentUser, session: SessionDep):
    return get_websites(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_website(user: CurrentUser, session: SessionDep):
    return get_websites(session, user, use_base_model=True)


@router.post("/")
async def create_website(
        user: CurrentUser, session: SessionDep, item: Website
):
    save_model(session, user, WebsiteModel.model_validate(item))


@router.put("/{item_id}")
async def update_website(
        user: CurrentUser, session: SessionDep, item_id: int, item: WebsitePost
):
    model_to_update = session.exec(
        select(WebsiteModel).where(WebsiteModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_website(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, WebsiteModel, item_id)
