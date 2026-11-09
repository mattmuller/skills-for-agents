"""Invoices."""


def _move(db, invoice_id: int, frm: str, to: str) -> bool:
    cur = db.execute("UPDATE invoices SET status = ? WHERE id = ? AND status = ?", (to, invoice_id, frm))
    return cur.rowcount == 1


def issue(db, invoice_id: int) -> bool:
    return _move(db, invoice_id, "draft", "issued")


def mark_paid(db, invoice_id: int) -> bool:
    return _move(db, invoice_id, "issued", "paid")


def void(db, invoice_id: int) -> bool:
    """Draft or issued invoices can be voided. Void is final by design."""
    return _move(db, invoice_id, "draft", "void") or _move(db, invoice_id, "issued", "void")
