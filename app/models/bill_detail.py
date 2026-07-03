from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BillDetail(Base):
    __tablename__ = "bill_detail"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("bill.id"), nullable=False, index=True)
    goods_id: Mapped[int | None] = mapped_column(ForeignKey("goods.id"), nullable=True, index=True)
    goods_name: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    buyer_id: Mapped[int | None] = mapped_column(ForeignKey("person.id"), nullable=True, index=True)
    buyer_other: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    bill: Mapped["Bill"] = relationship(back_populates="details")
    goods: Mapped["Goods | None"] = relationship(back_populates="bill_details")
    buyer: Mapped["Person | None"] = relationship(back_populates="bought_details", foreign_keys=[buyer_id])
