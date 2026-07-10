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
        bills = self.db.scalars(
            select(Bill)
            .join(Share, Share.bill_id == Bill.id)
            .where(Share.payer_id == user_id)
            .order_by(Bill.bill_date.desc(), Bill.id.desc())
            .distinct()
        ).all()

        total_bills = len(bills)
        paid_bills = len([bill for bill in bills if bill.paid_status])
        unpaid_bills = total_bills - paid_bills
        total_amount = sum((bill.total_value for bill in bills), Decimal("0"))

        shares = self.db.scalars(
            select(Share).where(Share.payer_id == user_id)
        ).all()
        user_balance = sum((share.net_value for share in shares), Decimal("0"))

        recent_bills = []
        for bill in bills[:5]:
            keeper = self.db.get(Person, bill.keeper_id) if bill.keeper_id else None
            recent_bills.append(
                RecentBill(
                    bill_id=bill.id,
                    total_value=bill.total_value,
                    bill_date=str(bill.bill_date),
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
