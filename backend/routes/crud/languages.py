from backend.database.crud import get_languages, delete_model, save_model
from backend.database.models import LanguageModel
from backend.schemas.endpoints import LanguagePost, Language
from backend.routes.deps import CurrentUser, SessionDep

from sqlmodel import select
from fastapi import APIRouter


router = APIRouter(prefix="/languages")


@router.get("/")
async def read_languages(user: CurrentUser, session: SessionDep):
    return get_languages(session, user, use_base_model=True)


@router.get("/{item_id}")
async def read_language(user: CurrentUser, session: SessionDep):
    return get_languages(session, user, use_base_model=True)


@router.post("/")
async def create_language(
        user: CurrentUser, session: SessionDep, item: Language
):
    save_model(session, user, LanguageModel.model_validate(item))


@router.put("/{item_id}")
async def update_language(
        user: CurrentUser, session: SessionDep, item_id: int, item: LanguagePost
):
    model_to_update = session.exec(
        select(LanguageModel).where(LanguageModel.id == item_id)
    ).one()

    model_to_update.sqlmodel_update(item)
    session.add(model_to_update)
    session.commit()
    session.refresh(model_to_update)

    return model_to_update


@router.delete("/{item_id}")
async def delete_language(user: CurrentUser, session: SessionDep, item_id: int):
    delete_model(session, user, LanguageModel, item_id)
