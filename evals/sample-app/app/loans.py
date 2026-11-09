"""Library book loans."""
from datetime import date


def open_loan(db, member_id: int, book_id: int, due: date) -> int:
    return db.insert(
        "INSERT INTO loans (member_id, book_id, due_date, status) VALUES (?, ?, ?, 'open')",
        (member_id, book_id, due),
    )


def renew_loan(db, loan_id: int, new_due: date) -> None:
    db.execute(
        "UPDATE loans SET due_date = ? WHERE id = ? AND status IN ('open', 'overdue')",
        (new_due, loan_id),
    )


def mark_overdue(db, today: date) -> None:
    """Nightly job."""
    db.execute(
        "UPDATE loans SET status = 'overdue' WHERE status = 'open' AND due_date < ?",
        (today,),
    )


def close_loan(db, loan_id: int) -> None:
    """Book returned."""
    db.execute("UPDATE loans SET status = 'closed' WHERE id = ?", (loan_id,))


def list_overdue(db):
    """Staff screen."""
    return db.query("SELECT * FROM loans WHERE status = 'overdue' ORDER BY due_date")
