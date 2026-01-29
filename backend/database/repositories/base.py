from abc import ABC

from pydantic import BaseModel
from sqlmodel import Session, select

from backend.database.models import BaseDatabaseModel, BaseUserConnectedData

# type SchemaModel[G: BaseModel] = G


class BaseRepository[T: BaseDatabaseModel, G: BaseModel](ABC):
    model: type[T]
    read_model: type[G]


class DataRepository[T: BaseUserConnectedData, G: BaseModel](
    BaseRepository[T, G]
):
    def read(self, session: Session, item_id: int | None) -> T:
        if self.__class__ is BaseRepository:
            raise Exception(
                "Cannot call this method on base class 'BaseRepository'"
            )

        if not item_id:
            raise Exception("item_id parameter cannot be None")

        row = session.exec(
            select(self.model).where(self.model.id == item_id)
        ).one()
        return row

    def read_all(self, session: Session, user_id: int | None) -> list[T]:
        if self.__class__ is BaseRepository:
            raise Exception(
                "Cannot call this method on base class 'BaseRepository'"
            )

        if not user_id:
            raise Exception("user_id parameter cannot be None")

        rows = session.exec(
            select(self.model).where(self.model.user_id == user_id)
        ).all()
        return list(rows)

    @staticmethod
    def create(session: Session, obj: T) -> T:
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @staticmethod
    def update(session: Session, obj: T, **kwargs) -> None:
        for key, val in kwargs.items():
            setattr(obj, key, val)
        session.add(obj)
        session.commit()

    @staticmethod
    def delete(session: Session, obj: T) -> None:
        session.delete(obj)
        session.commit()

    def convert_list_to_read_only(self, objs: list[T]) -> list[G]:
        return [self.read_model.model_validate(obj) for obj in objs]

    def convert_read_only(self, obj: T) -> G:
        return self.read_model.model_validate(obj)
