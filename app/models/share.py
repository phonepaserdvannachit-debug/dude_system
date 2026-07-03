from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Share(Base):
    __tablename__ = "share"
    __table_args__ = (UniqueConstraint("bill_id", "payer_id", name="uq_share_bill_payer"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("bill.id"), nullable=False, index=True)
    payer_id: Mapped[int | None] = mapped_column(ForeignKey("person.id"), nullable=True, index=True)
    payer_other: Mapped[str | None] = mapped_column(String(100), nullable=True)
    share_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    net_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    paid_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    bill: Mapped["Bill"] = relationship(back_populates="shares")
    payer: Mapped["Person | None"] = relationship(back_populates="shares", foreign_keys=[payer_id])
    slips: Mapped[List["Slip"]] = relationship(back_populates="share")
