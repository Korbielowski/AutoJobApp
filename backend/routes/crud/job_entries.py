# from backend.database.crud import get_job_entries, delete_model, save_model
# from backend.database.models import JobEntryModel
# from backend.schemas.endpoints import JobEntryPost, JobEntry
# from backend.routes.deps import CurrentUser, SessionDep
#
# from sqlmodel import select
# from fastapi import APIRouter
#
#
# router = APIRouter(prefix="job_entries")
#
#
# @router.get("/")
# async def read_job_entries(user: CurrentUser, session: SessionDep):
#     return get_job_entries(session, user, use_base_model=True)
#
#
# @router.get("/{item_id}")
# async def read_job_entry(user: CurrentUser, session: SessionDep):
#     return get_job_entries(session, user, use_base_model=True)
#
#
# @router.post("/")
# async def create_job_entry(
#         user: CurrentUser, session: SessionDep, item: JobEntry
# ):
#     save_model(session, user, JobEntryModel.model_validate(item))
#
#
# @router.put("/{item_id}")
# async def update_job_entry(
#         user: CurrentUser, session: SessionDep, item_id: int, item: JobEntryPost
# ):
#     model_to_update = session.exec(
#         select(JobEntryModel).where(JobEntryModel.id == item_id)
#     ).one()
#
#     model_to_update.sqlmodel_update(item)
#     session.add(model_to_update)
#     session.commit()
#     session.refresh(model_to_update)
#
#     return model_to_update
#
#
# @router.delete("/{item_id}")
# async def delete_job_entry(user: CurrentUser, session: SessionDep, item_id: int):
#     delete_model(session, user, JobEntryModel, item_id)
