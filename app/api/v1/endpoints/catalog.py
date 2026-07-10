from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.goods import Goods
from app.models.person import Person
from app.models.type_of_bill import TypeOfBill
from app.schemas.catalog import GoodsPublic, TypeOfBillPublic
from app.schemas.person import PersonPublic


router = APIRouter(tags=["Catalog"])


@router.get("/persons", response_model=list[PersonPublic])
def list_persons(
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> list[Person]:
    return db.scalars(select(Person).order_by(Person.name.asc())).all()


@router.get("/people", response_model=list[PersonPublic])
def list_people_alias(
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> list[Person]:
    return list_persons(db, current_user)


@router.get("/goods", response_model=list[GoodsPublic])
def list_goods(
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> list[Goods]:
    return db.scalars(select(Goods).where(Goods.is_active.is_(True)).order_by(Goods.name.asc())).all()


@router.get("/types", response_model=list[TypeOfBillPublic])
def list_types(
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> list[TypeOfBill]:
    return db.scalars(select(TypeOfBill).order_by(TypeOfBill.id.asc())).all()


@router.get("/type-of-bills", response_model=list[TypeOfBillPublic])
def list_type_of_bills_alias(
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> list[TypeOfBill]:
    return list_types(db, current_user)
