from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.person import Person
from app.models.share import Share
from app.models.slip import Slip
from app.schemas.slip import SlipDetailResponse, SlipUploadResponse
from app.core.config import settings
from app.services.notification_service import NotificationService
from app.services.storage_service import upload_file


MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpg",
    "image/jpeg",
}

ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
}


class SlipService:
    def __init__(self, db: Session):
        self.db = db

    async def upload_slip(
        self,
        share_id: int,
        file: UploadFile,
        current_user: Person,
    ) -> SlipUploadResponse:
        share = self.db.get(Share, share_id)

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found",
            )

        bill = self.db.get(Bill, share.bill_id)

        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found",
            )

        if not current_user.is_admin and share.payer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only upload slip for your own share",
            )

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required",
            )

        original_name = Path(file.filename).name
        file_suffix = Path(original_name).suffix.lower()

        if file_suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PNG, JPG, and JPEG files are allowed",
            )

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type",
            )

        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not exceed 50MB",
            )

        await file.seek(0)
        storage_url = upload_file(file, settings.SUPABASE_BUCKET_SLIPS)

        existing_slip = self.db.scalar(
            select(Slip).where(Slip.share_id == share.id)
        )

        if existing_slip:
            slip = existing_slip
            slip.storage_url = storage_url
            slip.file_name = original_name
            slip.file_type = file.content_type
            slip.file_size = file_size
        else:
            slip = Slip(
                share_id=share.id,
                storage_url=storage_url,
                file_name=original_name,
                file_type=file.content_type,
                file_size=file_size,
            )
            self.db.add(slip)

        share.paid_status = True

        if hasattr(share, "paid_at"):
            share.paid_at = datetime.now(timezone.utc)

        shares = self.db.scalars(
            select(Share).where(Share.bill_id == bill.id)
        ).all()

        all_paid = all(bool(item.paid_status) for item in shares)
        bill.paid_status = all_paid

        self.db.commit()
        self.db.refresh(slip)
        self.db.refresh(share)
        self.db.refresh(bill)
        NotificationService(self.db).notify_slip_uploaded(bill.id, share.payer_id)

        return SlipUploadResponse(
            slip_id=slip.id,
            share_id=share.id,
            bill_id=share.bill_id,
            payer_id=share.payer_id,
            storage_url=slip.storage_url,
            file_name=slip.file_name,
            file_type=slip.file_type,
            file_size=slip.file_size,
            paid_status=bool(share.paid_status),
            paid_at=getattr(share, "paid_at", None),
            bill_paid_status=bool(bill.paid_status),
        )

    def get_slip_by_share(
        self,
        share_id: int,
        current_user: Person,
    ) -> SlipDetailResponse:
        share = self.db.get(Share, share_id)

        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found",
            )

        if not current_user.is_admin and share.payer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own slip",
            )

        slip = self.db.scalar(
            select(Slip).where(Slip.share_id == share.id)
        )

        if not slip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slip not found",
            )

        return SlipDetailResponse(
            slip_id=slip.id,
            share_id=share.id,
            bill_id=share.bill_id,
            payer_id=share.payer_id,
            storage_url=slip.storage_url,
            file_name=slip.file_name,
            file_type=slip.file_type,
            file_size=slip.file_size,
            share_value=share.share_value,
            cost=share.cost,
            net_value=share.net_value,
            paid_status=bool(share.paid_status),
            created_at=getattr(slip, "created_at", None),
        )
