from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.person import Person
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/test")
def send_test_notification(
    db: Session = Depends(get_db),
    _: Person = Depends(require_admin),
) -> dict:
    return NotificationService(db).send_test_email()
