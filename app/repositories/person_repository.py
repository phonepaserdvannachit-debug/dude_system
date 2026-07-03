from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.person import Person


class PersonRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, person_id: int) -> Person | None:
        statement = select(Person).where(Person.id == person_id)
        return self.db.scalar(statement)

    def get_by_username(self, username: str) -> Person | None:
        normalized_username = username.strip().lower()
        statement = select(Person).where(Person.user_name == normalized_username)
        return self.db.scalar(statement)
