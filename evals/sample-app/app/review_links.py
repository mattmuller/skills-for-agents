"""Review links: an outside reader opens one document."""
import secrets
from datetime import datetime, timedelta

LINK_LIFETIME = timedelta(days=7)


def create_review_link(db, doc_id: int) -> str:
    token = secrets.token_urlsafe(24)
    db.insert(
        "INSERT INTO review_links (document_id, token, expires_at) VALUES (?, ?, ?)",
        (doc_id, token, datetime.utcnow() + LINK_LIFETIME),
    )
    return token


def revoke_review_link(db, token: str) -> None:
    db.execute("UPDATE review_links SET revoked = TRUE WHERE token = ?", (token,))


def open_document_by_token(db, token: str):
    link = db.query_one(
        "SELECT * FROM review_links WHERE token = ? AND revoked = FALSE", (token,)
    )
    if link is None:
        return None
    return db.query_one(
        "SELECT * FROM documents WHERE id = ? AND archived_at IS NULL", (link["document_id"],)
    )
