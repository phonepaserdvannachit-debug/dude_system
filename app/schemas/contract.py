from datetime import datetime

from pydantic import BaseModel, Field


class ContractMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ContractMessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str | None = None
    message: str
    is_read: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
