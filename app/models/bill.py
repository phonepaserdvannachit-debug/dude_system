from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Bill(Base):
    __tablename__ = "bill"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type_id: Mapped[int | None] = mapped_column(ForeignKey("type_of_bill.id"), nullable=True, index=True)
    total_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    paid_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    keeper_id: Mapped[int | None] = mapped_column(ForeignKey("person.id"), nullable=True, index=True)
    bookkeeper_auto: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    bill_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    type: Mapped["TypeOfBill | None"] = relationship(back_populates="bills")
    keeper: Mapped["Person | None"] = relationship(back_populates="kept_bills", foreign_keys=[keeper_id])
    details: Mapped[List["BillDetail"]] = relationship(back_populates="bill", cascade="all, delete-orphan")
    shares: Mapped[List["Share"]] = relationship(back_populates="bill", cascade="all, delete-orphan")
