from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.person import Person
from app.schemas.slip import SlipDetailResponse, SlipUploadResponse
from app.services.slip_service import SlipService


router = APIRouter(prefix="/slips", tags=["Slips"])


@router.post(
    "/shares/{share_id}",
    response_model=SlipUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_slip(
    share_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> SlipUploadResponse:
    service = SlipService(db)
    return await service.upload_slip(share_id, file, current_user)


@router.get(
    "/shares/{share_id}",
    response_model=SlipDetailResponse,
)
def get_slip_by_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> SlipDetailResponse:
    service = SlipService(db)
    return service.get_slip_by_share(share_id, current_user)