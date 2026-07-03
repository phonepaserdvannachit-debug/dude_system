from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.person import Person
from app.services.storage_service import upload_file
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])


# -------------------------
# PROFILE UPLOAD
# -------------------------
@router.post("/profile")
def upload_profile(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Person = Depends(get_current_user)
):
    url = upload_file(file, settings.SUPABASE_BUCKET_PROFILES)

    user.profile_pic = url
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "Profile uploaded successfully",
        "profile_pic": url
    }


# -------------------------
# QR UPLOAD
# -------------------------
@router.post("/qr")
def upload_qr(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Person = Depends(get_current_user)
):
    url = upload_file(file, settings.SUPABASE_BUCKET_QR)

    user.qr_code = url
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "QR uploaded successfully",
        "qr_code": url
    }