from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.person import Person
from app.schemas.bill import (
    BillCreateRequest,
    BillCreateResponse,
    BillDetailResponse,
    BillListItem,
    BillUpdateRequest,
)
from app.services.bill_service import BillService


router = APIRouter(prefix="/bills", tags=["Bills"])


@router.get("", response_model=list[BillListItem])
def list_bills(
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> list[BillListItem]:
    service = BillService(db)
    return service.list_bills(current_user)


@router.get("/{bill_id}", response_model=BillDetailResponse)
def get_bill_detail(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> BillDetailResponse:
    service = BillService(db)
    return service.get_bill_detail(bill_id, current_user)


@router.post(
    "",
    response_model=BillCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bill(
    payload: BillCreateRequest,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> BillCreateResponse:
    service = BillService(db)
    return service.create_bill(payload)


@router.put("/{bill_id}", response_model=BillDetailResponse)
def update_bill(
    bill_id: int,
    payload: BillUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> BillDetailResponse:
    service = BillService(db)
    return service.update_bill(bill_id, payload, current_user)
