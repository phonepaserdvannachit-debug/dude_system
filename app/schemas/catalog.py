from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class GoodsPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal | None = None
    category_id: int | None = None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TypeOfBillPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type_name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
