"""Warehouse shipments."""


def create_shipment(db, order_ref: str) -> int:
    return db.insert("INSERT INTO shipments (order_ref, status) VALUES (?, 'packed')", (order_ref,))


def set_status(db, shipment_id: int, status: str) -> None:
    """Called by the scanner API with whatever the scanner reports."""
    db.execute("UPDATE shipments SET status = ? WHERE id = ?", (status, shipment_id))


def list_in_transit(db):
    return db.query("SELECT * FROM shipments WHERE status = 'shipped'")


def list_awaiting_dispatch(db):
    return db.query("SELECT * FROM shipments WHERE status = 'packed'")
