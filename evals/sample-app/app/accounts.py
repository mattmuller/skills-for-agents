"""Account suspension."""
from datetime import datetime


def suspend_account(db, account_id: int, actor: str) -> None:
    """Staff action. Revokes API access immediately."""
    db.execute(
        "UPDATE accounts SET status = 'suspended', suspended_at = ? WHERE id = ?",
        (datetime.utcnow(), account_id),
    )
    db.execute("DELETE FROM api_tokens WHERE account_id = ?", (account_id,))


def get_account_for_token(db, token: str):
    row = db.query_one(
        "SELECT a.* FROM accounts a JOIN api_tokens t ON t.account_id = a.id "
        "WHERE t.token = ? AND a.status = 'active'",
        (token,),
    )
    return row
