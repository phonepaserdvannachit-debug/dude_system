from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    aka: Mapped[str | None] = mapped_column(String(50), nullable=True)
    profile_pic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    qr_code: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    kept_bills: Mapped[List["Bill"]] = relationship(back_populates="keeper", foreign_keys="Bill.keeper_id")
    bought_details: Mapped[List["BillDetail"]] = relationship(back_populates="buyer", foreign_keys="BillDetail.buyer_id")
    shares: Mapped[List["Share"]] = relationship(back_populates="payer", foreign_keys="Share.payer_id")
    slips_uploaded: Mapped[List["Slip"]] = relationship(back_populates="uploaded_by", foreign_keys="Slip.uploaded_by_id")
    messages: Mapped[List["Contract"]] = relationship(back_populates="sender", foreign_keys="Contract.sender_id")
