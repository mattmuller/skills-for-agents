"""Subscriptions."""
from datetime import datetime, timedelta

GRACE = timedelta(days=14)


def activate(db, sub_id: int, paid_until: datetime) -> None:
    db.execute(
        "UPDATE subscriptions SET status = 'active', expires_at = ?, past_due_since = NULL "
        "WHERE id = ? AND status IN ('trialing', 'past_due')",
        (paid_until, sub_id),
    )
    db.execute("UPDATE entitlements SET revoked_at = NULL WHERE subscription_id = ?", (sub_id,))


def payment_failed(db, sub_id: int, now: datetime) -> None:
    db.execute(
        "UPDATE subscriptions SET status = 'past_due', past_due_since = ? "
        "WHERE id = ? AND status = 'active'",
        (now, sub_id),
    )


def cancel(db, sub_id: int, now: datetime) -> None:
    db.execute(
        "UPDATE subscriptions SET status = 'canceled' WHERE id = ? AND status != 'canceled'",
        (sub_id,),
    )
    db.execute("UPDATE entitlements SET revoked_at = ? WHERE subscription_id = ?", (now, sub_id))


def expire_past_due(db, now: datetime) -> None:
    """Nightly job: cancel subscriptions past due for longer than the grace period."""
    for sub in db.query(
        "SELECT id FROM subscriptions WHERE status = 'past_due' AND past_due_since < ?",
        (now - GRACE,),
    ):
        cancel(db, sub["id"], now)


def is_entitled(db, sub_id: int, feature: str, now: datetime) -> bool:
    return (
        db.query_one(
            "SELECT 1 FROM subscriptions s JOIN entitlements e ON e.subscription_id = s.id "
            "WHERE s.id = ? AND e.feature = ? AND e.revoked_at IS NULL "
            "AND s.status IN ('trialing', 'active', 'past_due') AND s.expires_at > ?",
            (sub_id, feature, now),
        )
        is not None
    )
