from app.schemas.bill import (
    BillCreateRequest,
    BillCreateResponse,
    BillDetailItem,
    BillDetailResponse,
    BillListItem,
    BillShareDetail,
    ShareResult,
)
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bill import Bill
from app.models.bill_detail import BillDetail
from app.models.person import Person
from app.models.share import Share
from app.models.type_of_bill import TypeOfBill
from app.schemas.bill import BillCreateRequest, BillCreateResponse, ShareResult


MONEY = Decimal("0.01")


class BillService:
    def __init__(self, db: Session):
        self.db = db

    def _get_share_status(self, net_value: Decimal) -> str:
        if net_value < 0:
            return "PAY"
        if net_value > 0:
            return "RECEIVE"
        return "CLEAR"

    def list_bills(self) -> list[BillListItem]:
        bills = self.db.scalars(
            select(Bill).order_by(Bill.bill_date.desc(), Bill.id.desc())
        ).all()

        results: list[BillListItem] = []

        for bill in bills:
            keeper = self.db.get(Person, bill.keeper_id) if bill.keeper_id else None

            shares = self.db.scalars(
                select(Share).where(Share.bill_id == bill.id)
            ).all()

            results.append(
                BillListItem(
                    bill_id=bill.id,
                    bill_date=bill.bill_date,
                    total_value=bill.total_value,
                    keeper_id=bill.keeper_id,
                    keeper_name=keeper.name if keeper else None,
                    paid_status=bool(bill.paid_status),
                    sharer_count=len(shares),
                )
            )

        return results

    def get_bill_detail(self, bill_id: int) -> BillDetailResponse:
        bill = self.db.get(Bill, bill_id)

        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bill not found",
            )

        details = self.db.scalars(
            select(BillDetail).where(BillDetail.bill_id == bill.id)
        ).all()

        shares = self.db.scalars(
            select(Share).where(Share.bill_id == bill.id)
        ).all()

        person_ids = set()

        if bill.keeper_id:
            person_ids.add(bill.keeper_id)

        for detail in details:
            person_ids.add(detail.buyer_id)

        for share in shares:
            person_ids.add(share.payer_id)

        people = self.db.scalars(
            select(Person).where(Person.id.in_(person_ids))
        ).all() if person_ids else []

        people_map = {person.id: person for person in people}

        keeper = people_map.get(bill.keeper_id)

        item_results = [
            BillDetailItem(
                id=detail.id,
                goods_id=detail.goods_id,
                goods_name=detail.goods_name,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                line_total=detail.line_total,
                buyer_id=detail.buyer_id,
                buyer_name=people_map.get(detail.buyer_id).name
                if people_map.get(detail.buyer_id)
                else None,
                reason=detail.reason,
            )
            for detail in details
        ]

        share_results = [
            BillShareDetail(
                id=share.id,
                person_id=share.payer_id,
                person_name=people_map.get(share.payer_id).name
                if people_map.get(share.payer_id)
                else None,
                share_value=share.share_value,
                cost=share.cost,
                net_value=share.net_value,
                status=self._get_share_status(share.net_value),
                paid_status=bool(share.paid_status),
            )
            for share in shares
        ]

        return BillDetailResponse(
            bill_id=bill.id,
            type_id=bill.type_id,
            bill_date=bill.bill_date,
            total_value=bill.total_value,
            keeper_id=bill.keeper_id,
            keeper_name=keeper.name if keeper else None,
            paid_status=bool(bill.paid_status),
            bookkeeper_auto=bool(bill.bookkeeper_auto),
            items=item_results,
            shares=share_results,
        )

    def create_bill(self, payload: BillCreateRequest) -> BillCreateResponse:
        sharer_ids = list(dict.fromkeys(payload.sharer_ids))

        if not sharer_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one sharer is required",
            )

        buyer_ids = [item.buyer_id for item in payload.items]
        all_person_ids = set(sharer_ids + buyer_ids)

        if payload.manual_keeper_id:
            all_person_ids.add(payload.manual_keeper_id)

        existing_people = set(
            self.db.scalars(
                select(Person.id).where(Person.id.in_(all_person_ids))
            ).all()
        )

        missing_people = all_person_ids - existing_people
        if missing_people:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Person not found: {sorted(missing_people)}",
            )

        for buyer_id in buyer_ids:
            if buyer_id not in sharer_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Buyer {buyer_id} must also be included in sharer_ids",
                )

        if payload.type_id is not None:
            type_exists = self.db.scalar(
                select(TypeOfBill.id).where(TypeOfBill.id == payload.type_id)
            )
            if not type_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid type_id",
                )

        try:
            total_value = Decimal("0.00")
            cost_map: dict[int, Decimal] = {
                person_id: Decimal("0.00") for person_id in sharer_ids
            }

            calculated_items = []

            for item in payload.items:
                quantity = Decimal(item.quantity)
                unit_price = Decimal(item.unit_price)
                line_total = (quantity * unit_price).quantize(MONEY, ROUND_HALF_UP)

                total_value += line_total
                cost_map[item.buyer_id] += line_total

                calculated_items.append(
                    {
                        "goods_id": item.goods_id,
                        "goods_name": item.goods_name,
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "line_total": line_total,
                        "buyer_id": item.buyer_id,
                        "reason": item.reason,
                    }
                )

            total_value = total_value.quantize(MONEY, ROUND_HALF_UP)

            if payload.auto_bookkeeper:
                keeper_id = max(cost_map, key=lambda person_id: cost_map[person_id])
            else:
                if payload.manual_keeper_id is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="manual_keeper_id is required when auto_bookkeeper is false",
                    )
                keeper_id = payload.manual_keeper_id

            share_value = (total_value / Decimal(len(sharer_ids))).quantize(
                MONEY, ROUND_HALF_UP
            )

            bill = Bill(
                type_id=payload.type_id,
                total_value=total_value,
                paid_status=False,
                keeper_id=keeper_id,
                bookkeeper_auto=payload.auto_bookkeeper,
                bill_date=payload.bill_date,
            )

            self.db.add(bill)
            self.db.flush()

            for item in calculated_items:
                detail = BillDetail(
                    bill_id=bill.id,
                    goods_id=item["goods_id"],
                    goods_name=item["goods_name"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    line_total=item["line_total"],
                    buyer_id=item["buyer_id"],
                    reason=item["reason"],
                )
                self.db.add(detail)

            share_results: list[ShareResult] = []

            for person_id in sharer_ids:
                cost = cost_map[person_id].quantize(MONEY, ROUND_HALF_UP)
                net_value = (cost - share_value).quantize(MONEY, ROUND_HALF_UP)

                if net_value < 0:
                    share_status = "PAY"
                    paid_status = False
                elif net_value > 0:
                    share_status = "RECEIVE"
                    paid_status = True
                else:
                    share_status = "CLEAR"
                    paid_status = True

                share = Share(
                    bill_id=bill.id,
                    payer_id=person_id,
                    share_value=share_value,
                    cost=cost,
                    net_value=net_value,
                    paid_status=paid_status,
                )
                self.db.add(share)

                share_results.append(
                    ShareResult(
                        person_id=person_id,
                        cost=cost,
                        share_value=share_value,
                        net_value=net_value,
                        status=share_status,
                        paid_status=paid_status,
                    )
                )

            self.db.commit()
            self.db.refresh(bill)

            return BillCreateResponse(
                bill_id=bill.id,
                total_value=total_value,
                keeper_id=keeper_id,
                share_value=share_value,
                shares=share_results,
            )

        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create bill: {exc}",
            ) from exc