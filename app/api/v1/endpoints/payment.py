from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.person import Person
from app.schemas.payment import BillPaymentStatusResponse, SharePaymentResponse
from app.services.payment_service import PaymentService


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.patch(
    "/shares/{share_id}/confirm",
    response_model=SharePaymentResponse,
    status_code=status.HTTP_200_OK,
)
def confirm_share_payment(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> SharePaymentResponse:
    service = PaymentService(db)
    return service.confirm_share_payment(share_id, current_user)


@router.get(
    "/bills/{bill_id}/status",
    response_model=BillPaymentStatusResponse,
)
def get_bill_payment_status(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> BillPaymentStatusResponse:
    service = PaymentService(db)
    return service.get_bill_payment_status(bill_id)