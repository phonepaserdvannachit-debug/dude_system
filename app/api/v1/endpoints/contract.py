from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.contract import Contract
from app.models.person import Person
from app.schemas.contract import ContractMessageCreate, ContractMessageResponse


router = APIRouter(prefix="/contracts", tags=["Contracts"])


def _message_response(message: Contract) -> ContractMessageResponse:
    return ContractMessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        sender_name=message.sender.name if message.sender else None,
        message=message.message,
        is_read=bool(message.is_read),
        created_at=message.created_at,
        updated_at=message.updated_at,
    )


@router.get("", response_model=list[ContractMessageResponse])
def list_contract_messages(
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> list[ContractMessageResponse]:
    messages = db.scalars(
        select(Contract).order_by(Contract.created_at.asc(), Contract.id.asc())
    ).all()
    return [_message_response(message) for message in messages]


@router.post(
    "",
    response_model=ContractMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract_message(
    payload: ContractMessageCreate,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> ContractMessageResponse:
    message = Contract(sender_id=current_user.id, message=payload.message)
    db.add(message)
    db.commit()
    db.refresh(message)
    return _message_response(message)


@router.patch("/{message_id}/read", response_model=ContractMessageResponse)
def mark_contract_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: Person = Depends(get_current_user),
) -> ContractMessageResponse:
    message = db.get(Contract, message_id)
    if message is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    message.is_read = True
    db.commit()
    db.refresh(message)
    return _message_response(message)
