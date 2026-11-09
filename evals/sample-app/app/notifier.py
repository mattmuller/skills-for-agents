"""Scheduled notices."""
from datetime import date

MAX_NOTICES = 3


def send_overdue_notices(db, mailer, today: date) -> int:
    """Nightly job: remind members whose loan is past its due date."""
    loans = db.query(
        "SELECT * FROM loans WHERE due_date < ? AND notices_sent < ?",
        (today, MAX_NOTICES),
    )
    for loan in loans:
        mailer.send(loan["member_id"], "overdue-notice", {"loan_id": loan["id"]})
        db.execute("UPDATE loans SET notices_sent = notices_sent + 1 WHERE id = ?", (loan["id"],))
    return len(loans)


def send_invoice_reminders(db, mailer, today: date) -> int:
    invoices = db.query(
        "SELECT * FROM invoices WHERE status = 'issued' AND due_date < ?", (today,)
    )
    for inv in invoices:
        mailer.send(inv["account_id"], "invoice-reminder", {"invoice_id": inv["id"]})
    return len(invoices)
