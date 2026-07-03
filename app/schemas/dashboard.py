from decimal import Decimal
from pydantic import BaseModel


class RecentBill(BaseModel):
    bill_id: int
    total_value: Decimal
    bill_date: str
    keeper_name: str | None


class DashboardResponse(BaseModel):
    total_bills: int
    paid_bills: int
    unpaid_bills: int
    total_amount: Decimal
    user_balance: Decimal
    recent_bills: list[RecentBill]