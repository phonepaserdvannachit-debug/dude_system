from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.person import Person
from app.models.share import Share
from app.schemas.dashboard import DashboardResponse, RecentBill


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self, user_id: int) -> DashboardResponse:

        bills = self.db.scalars(select(Bill)).all()

        total_bills = len(bills)
        paid_bills = len([b for b in bills if b.paid_status])
        unpaid_bills = total_bills - paid_bills

        total_amount = sum((b.total_value for b in bills), Decimal("0"))

        shares = self.db.scalars(
            select(Share).where(Share.payer_id == user_id)
        ).all()

        user_balance = sum((s.net_value for s in shares), Decimal("0"))

        recent = (
            sorted(bills, key=lambda x: x.id, reverse=True)[:5]
            if bills
            else []
        )

        recent_bills = []
        for b in recent:
            keeper = self.db.get(Person, b.keeper_id) if b.keeper_id else None

            recent_bills.append(
                RecentBill(
                    bill_id=b.id,
                    total_value=b.total_value,
                    bill_date=str(b.bill_date),
                    keeper_name=keeper.name if keeper else None,
                )
            )

        return DashboardResponse(
            total_bills=total_bills,
            paid_bills=paid_bills,
            unpaid_bills=unpaid_bills,
            total_amount=total_amount,
            user_balance=user_balance,
            recent_bills=recent_bills,
        )