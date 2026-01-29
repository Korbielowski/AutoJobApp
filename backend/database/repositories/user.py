from sqlmodel import Session, select

from backend.database.models import UserModel
from backend.database.repositories.base import BaseRepository
from backend.schemas.models import User


class UserRepository(BaseRepository[UserModel, User]):
    model = UserModel
    read_model = User

    @staticmethod
    def create(session: Session, user: UserModel) -> UserModel:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def delete_user(session: Session, email: str) -> None:
        session.delete(
            session.exec(
                select(UserModel).where(UserModel.email == email)
            ).first()
        )
        session.commit()

    @staticmethod
    def get_users(session: Session) -> list[UserModel]:
        output = session.exec(select(UserModel)).all()
        return list(output)

    # def convert_to_read_only(self) -> User:
