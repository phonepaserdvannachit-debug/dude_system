from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Slip(Base):
    __tablename__ = "slip"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    share_id: Mapped[int] = mapped_column(ForeignKey("share.id"), nullable=False, index=True)
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("person.id"), nullable=True, index=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    share: Mapped["Share"] = relationship(back_populates="slips")
    uploaded_by: Mapped["Person | None"] = relationship(back_populates="slips_uploaded", foreign_keys=[uploaded_by_id])
