from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SharePaymentResponse(BaseModel):
    share_id: int
    bill_id: int
    payer_id: int
    share_value: Decimal
    cost: Decimal
    net_value: Decimal
    paid_status: bool
    paid_at: datetime | None
    bill_paid_status: bool


class BillPaymentStatusResponse(BaseModel):
    bill_id: int
    paid_status: bool
    total_shares: int
    paid_shares: int
    unpaid_shares: int