"""Documents in review."""
from datetime import datetime


def archive_document(db, doc_id: int) -> None:
    now = datetime.utcnow()
    db.execute("UPDATE documents SET archived_at = ? WHERE id = ?", (now, doc_id))
    db.execute(
        "UPDATE attachments SET archived_at = ? WHERE document_id = ? AND archived_at IS NULL",
        (now, doc_id),
    )


def restore_document(db, doc_id: int) -> None:
    db.execute("UPDATE documents SET archived_at = NULL WHERE id = ?", (doc_id,))


def list_attachments(db, doc_id: int):
    return db.query(
        "SELECT * FROM attachments WHERE document_id = ? AND archived_at IS NULL", (doc_id,)
    )
