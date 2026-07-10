from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class BillItemCreate(BaseModel):
    goods_id: int | None = None
    goods_name: str = Field(min_length=1, max_length=100)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    buyer_id: int
    reason: str | None = None


class BillCreateRequest(BaseModel):
    type_id: int | None = None
    bill_date: date
    auto_bookkeeper: bool = True
    manual_keeper_id: int | None = None
    sharer_ids: list[int] = Field(min_length=1)
    items: list[BillItemCreate] = Field(min_length=1)


class BillUpdateRequest(BillCreateRequest):
    pass


class ShareResult(BaseModel):
    person_id: int
    cost: Decimal
    share_value: Decimal
    net_value: Decimal
    status: Literal["PAY", "RECEIVE", "CLEAR"]
    paid_status: bool


class BillCreateResponse(BaseModel):
    bill_id: int
    total_value: Decimal
    keeper_id: int
    share_value: Decimal
    shares: list[ShareResult]


class BillListItem(BaseModel):
    bill_id: int
    bill_date: date
    total_value: Decimal
    keeper_id: int | None
    keeper_name: str | None
    paid_status: bool
    sharer_count: int


class BillDetailItem(BaseModel):
    id: int
    goods_id: int | None
    goods_name: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    buyer_id: int
    buyer_name: str | None
    reason: str | None


class BillShareDetail(BaseModel):
    id: int
    person_id: int
    person_name: str | None
    share_value: Decimal
    cost: Decimal
    net_value: Decimal
    status: Literal["PAY", "RECEIVE", "CLEAR"]
    paid_status: bool


class BillDetailResponse(BaseModel):
    bill_id: int
    type_id: int | None
    bill_date: date
    total_value: Decimal
    keeper_id: int | None
    keeper_name: str | None
    paid_status: bool
    bookkeeper_auto: bool
    items: list[BillDetailItem]
    shares: list[BillShareDetail]
