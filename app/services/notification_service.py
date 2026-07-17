from decimal import Decimal
from html import escape

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.bill import Bill
from app.models.person import Person
from app.models.share import Share


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def notify_bill_created(self, bill_id: int) -> None:
        self._send_bill_notice(bill_id, "New bill created")

    def notify_bill_updated(self, bill_id: int) -> None:
        self._send_bill_notice(bill_id, "Bill updated")

    def notify_slip_uploaded(self, bill_id: int, payer_id: int | None) -> None:
        bill = self.db.get(Bill, bill_id)
        if not bill:
            return

        payer = self.db.get(Person, payer_id) if payer_id else None
        keeper = self.db.get(Person, bill.keeper_id) if bill.keeper_id else None
        payer_name = payer.name if payer else "A sharer"
        keeper_name = keeper.name if keeper else "book keeper"

        subject = f"Payment slip uploaded for bill #{bill.id}"
        html = f"""
        <h2>Payment slip uploaded</h2>
        <p>{escape(payer_name)} uploaded a slip for bill #{bill.id}.</p>
        <p><strong>Book keeper:</strong> {escape(keeper_name)}</p>
        <p><strong>Bill date:</strong> {bill.bill_date}</p>
        <p><strong>Total:</strong> {self._money(bill.total_value)} Kip</p>
        """
        self._send_email(subject, html)

    def send_test_email(self) -> dict:
        result = self._send_email(
            "DUDE email notification test",
            """
            <h2>DUDE email test</h2>
            <p>If you receive this, Railway and Resend are connected.</p>
            """,
            raise_errors=True,
        )
        return {"sent": True, "resend": result}

    def _send_bill_notice(self, bill_id: int, title: str) -> None:
        bill = self.db.get(Bill, bill_id)
        if not bill:
            return

        keeper = self.db.get(Person, bill.keeper_id) if bill.keeper_id else None
        shares = self.db.scalars(
            select(Share).where(Share.bill_id == bill.id)
        ).all()

        rows = []
        for share in shares:
            payer = self.db.get(Person, share.payer_id) if share.payer_id else None
            rows.append(
                "<tr>"
                f"<td>{escape(payer.name if payer else 'Unknown')}</td>"
                f"<td>{self._money(share.cost)} Kip</td>"
                f"<td>{self._money(share.share_value)} Kip</td>"
                f"<td>{self._money(share.net_value)} Kip</td>"
                "</tr>"
            )

        subject = f"{title}: bill #{bill.id}"
        html = f"""
        <h2>{escape(title)}</h2>
        <p>A bill was saved in DUDE Payment Sharing System.</p>
        <p><strong>Bill:</strong> #{bill.id}</p>
        <p><strong>Date:</strong> {bill.bill_date}</p>
        <p><strong>Total:</strong> {self._money(bill.total_value)} Kip</p>
        <p><strong>Book keeper:</strong> {escape(keeper.name if keeper else 'Unknown')}</p>
        <table cellpadding="8" cellspacing="0" border="1">
          <thead>
            <tr>
              <th>Sharer</th>
              <th>Cost</th>
              <th>Share</th>
              <th>Net</th>
            </tr>
          </thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
        """
        self._send_email(subject, html)

    def _send_email(
        self,
        subject: str,
        html: str,
        raise_errors: bool = False,
    ) -> bool | dict:
        if not settings.RESEND_API_KEY or not settings.NOTIFICATION_TEST_EMAIL:
            if raise_errors:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing RESEND_API_KEY or NOTIFICATION_TEST_EMAIL",
                )
            return False

        try:
            response = httpx.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.EMAIL_FROM,
                    "to": [settings.NOTIFICATION_TEST_EMAIL],
                    "subject": subject,
                    "html": html,
                },
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if raise_errors:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail={
                        "status_code": exc.response.status_code,
                        "resend_response": exc.response.text,
                    },
                ) from exc
            return False
        except Exception as exc:
            if raise_errors:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=str(exc),
                ) from exc
            return False

    def _money(self, value: Decimal | int | float | None) -> str:
        if value is None:
            return "0"
        return f"{Decimal(value):,.0f}"
