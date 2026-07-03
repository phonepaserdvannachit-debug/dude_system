from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.person import Person
from app.models.share import Share
from app.schemas.payment import BillPaymentStatusResponse, SharePaymentResponse


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def confirm_share_payment(
        self,
        share_id: int,
        current_user: Person,
    ) -> SharePaymentResponse:
        share = self.db.get(Share, share_id)

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found",
            )

        bill = self.db.get(Bill, share.bill_id)

        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found",
            )

        if not current_user.is_admin and share.payer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only confirm your own payment",
            )

        share.paid_status = True

        if hasattr(share, "paid_at"):
            share.paid_at = datetime.now(timezone.utc)

        shares = self.db.scalars(
            select(Share).where(Share.bill_id == bill.id)
        ).all()

        all_paid = all(bool(item.paid_status) for item in shares)

        bill.paid_status = all_paid

        self.db.commit()
        self.db.refresh(share)
        self.db.refresh(bill)

        return SharePaymentResponse(
            share_id=share.id,
            bill_id=share.bill_id,
            payer_id=share.payer_id,
            share_value=share.share_value,
            cost=share.cost,
            net_value=share.net_value,
            paid_status=bool(share.paid_status),
            paid_at=getattr(share, "paid_at", None),
            bill_paid_status=bool(bill.paid_status),
        )

    def get_bill_payment_status(self, bill_id: int) -> BillPaymentStatusResponse:
        bill = self.db.get(Bill, bill_id)

        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found",
            )

        shares = self.db.scalars(
            select(Share).where(Share.bill_id == bill.id)
        ).all()

        total_shares = len(shares)
        paid_shares = len([share for share in shares if share.paid_status])
        unpaid_shares = total_shares - paid_shares

        return BillPaymentStatusResponse(
            bill_id=bill.id,
            paid_status=bool(bill.paid_status),
            total_shares=total_shares,
            paid_shares=paid_shares,
            unpaid_shares=unpaid_shares,
        )