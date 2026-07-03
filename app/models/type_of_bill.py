from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TypeOfBill(Base):
    __tablename__ = "type_of_bill"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    bills: Mapped[List["Bill"]] = relationship(back_populates="type")
