from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.person import Person
from app.repositories.person_repository import PersonRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.people = PersonRepository(db)

    def authenticate(self, username: str, password: str) -> Person:
        person = self.people.get_by_username(username)
        if person is None or not person.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not verify_password(password, person.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        return person

    def create_login_token(self, person: Person) -> str:
        return create_access_token(
            subject=person.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
