"""Support tickets."""
from datetime import datetime


def _move(db, ticket_id: int, allowed_from: tuple, to: str) -> bool:
    marks = ",".join("?" for _ in allowed_from)
    cur = db.execute(
        f"UPDATE tickets SET status = ? WHERE id = ? AND status IN ({marks})",
        (to, ticket_id, *allowed_from),
    )
    return cur.rowcount == 1


def open_ticket(db, ticket_id: int) -> bool:
    return _move(db, ticket_id, ("new",), "open")


def resolve_ticket(db, ticket_id: int) -> bool:
    return _move(db, ticket_id, ("open",), "resolved")


def close_ticket(db, ticket_id: int) -> bool:
    return _move(db, ticket_id, ("resolved",), "closed")


def reopen_ticket(db, ticket_id: int) -> bool:
    return _move(db, ticket_id, ("resolved",), "open")


def escalate_ticket(db, ticket_id: int) -> bool:
    if _move(db, ticket_id, ("open",), "escalating"):
        db.insert(
            "INSERT INTO escalations (ticket_id, opened_at) VALUES (?, ?)",
            (ticket_id, datetime.utcnow()),
        )
        return True
    return False


def finish_escalation(db, ticket_id: int) -> bool:
    """Second line hands the ticket back."""
    db.execute(
        "UPDATE escalations SET closed_at = ? WHERE ticket_id = ? AND closed_at IS NULL",
        (datetime.utcnow(), ticket_id),
    )
    return _move(db, ticket_id, ("escalating",), "open")


def on_event(db, event: dict) -> None:
    """Event bus handler registered at start-up."""
    if event["type"] == "ticket.escalation_done":
        finish_escalation(db, event["ticket_id"])
