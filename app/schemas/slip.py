from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class SlipUploadResponse(BaseModel):
    slip_id: int
    share_id: int
    bill_id: int
    payer_id: int
    storage_url: str
    file_name: str
    file_type: str
    file_size: int
    paid_status: bool
    paid_at: datetime | None
    bill_paid_status: bool


class SlipDetailResponse(BaseModel):
    slip_id: int
    share_id: int
    bill_id: int
    payer_id: int
    storage_url: str
    file_name: str
    file_type: str
    file_size: int
    share_value: Decimal
    cost: Decimal
    net_value: Decimal
    paid_status: bool
    created_at: datetime | None