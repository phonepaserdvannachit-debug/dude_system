from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PersonPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    aka: str | None = None
    profile_pic: str | None = None
    user_name: str
    qr_code: str | None = None
    is_admin: bool
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
