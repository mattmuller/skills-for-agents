# State-transition audit: bs1/app

Read: schema.sql, docs/rules.md, all 9 files in app/. Nothing was run; every finding is from reading the code against docs/rules.md. Only these files exist, so "no caller found" means no caller inside this directory.

## High

### 1. Reinstating a suspended account cannot restore access
- Where: app/accounts.py `suspend_account` (line 11). There is no `reinstate_account` anywhere in app/.
- Reach: staff suspend an account (staff action). The function deletes every row in `api_tokens`. Reinstating later (status back to 'active') cannot bring the tokens back, because they no longer exist. The customer's integrations stay broken until new tokens are issued.
- Rule broken: "A reinstated account gets back full access."
- Also: no reinstate path exists, and `suspended_at` is never cleared. Suspending twice overwrites `suspended_at`.
- Fix: keep the tokens and let `get_account_for_token` (already checks `status = 'active'`) deny them. Add a `reinstate_account` that clears `suspended_at`.

### 2. Expired review links keep working forever
- Where: app/review_links.py `open_document_by_token` (lines 22-24). It checks `revoked = FALSE` but never checks `expires_at`.
- Reach: any outside reader who holds a link can open the document after the 7 days. Anyone the link was forwarded to can too. No job sets `revoked` on expiry, so nothing else closes it.
- Rule broken: "open one document for seven days." This exposes document content (access control).
- Fix: add `AND expires_at > ?` to the query.

### 3. Renewal payments on an active subscription are ignored
- Where: app/subscriptions.py `activate` (line 10), guard `status IN ('trialing','past_due')`.
- Reach: a payment webhook for an already-active subscription (normal renewal) matches no row, so `expires_at` is never extended. `is_entitled` requires `expires_at > now`, so a paying customer loses access when the first period ends.
- Caveat: if renewal is handled by code outside this directory, this drops to Medium. Nothing in app/ extends `expires_at` otherwise.

### 4. Shipment status accepts any value in any order
- Where: app/shipments.py `set_status` (line 10); schema.sql has no CHECK on `shipments.status`.
- Reach: the scanner API passes whatever the scanner reports. A re-scan can move delivered back to shipped or packed. Duplicate or out-of-order scans do the same. A typo or unknown string (for example "Shipped") matches neither `list_in_transit` nor `list_awaiting_dispatch`, so the shipment disappears from both screens. A late packed scan can make an already dispatched parcel look awaiting dispatch and get dispatched twice.
- Rule broken: packed -> shipped -> delivered only.
- Fix: use a guarded `_move` like invoices.py and tickets.py, with an allow-list of statuses.

## Medium

### 5. Closed loans still get overdue notices
- Where: app/notifier.py `send_overdue_notices` (lines 9-12). The query has no `status` filter.
- Reach: nightly job. A member returns a book (`close_loan`), `due_date` is still in the past, and `notices_sent < 3`. They then receive up to three "overdue" emails for a book they returned.
- Rule broken: "Closing a loan stops all notices for it."
- Fix: add `AND status != 'closed'` (or `IN ('open','overdue')`).

### 6. Restoring a document does not restore its attachments
- Where: app/documents.py `restore_document` (line 15). It only clears the document's `archived_at`.
- Reach: staff archive then restore a document. `list_attachments` filters `archived_at IS NULL`, so all attachments stay hidden after the restore.
- Rule broken: "Restoring a document brings it and its attachments back."
- Related trap when fixing: `archive_document` only stamps attachments that were not already archived. A naive "restore all attachments" would also bring back attachments someone archived on purpose earlier. Restore only rows where `archived_at` equals the document's archive timestamp.
- Both functions run two statements with no transaction visible here, so a failure between them leaves a half-archived document.

### 7. Late payment on a canceled subscription: entitlements come back, status does not
- Where: app/subscriptions.py `activate` (line 13). The entitlements UPDATE is unconditional; the status UPDATE is guarded.
- Reach: a payment webhook arrives after the nightly job canceled the subscription (or a retry hits a canceled one). The status stays 'canceled' (correct, final by design), but entitlement rows get `revoked_at = NULL`. `is_entitled` still says no, because it checks status. The customer who paid gets nothing, and the rows now disagree with the subscription. Any other reader of `entitlements` will treat them as live.
- Fix: do the entitlement update only if the status update changed a row, and surface "paid but canceled" so someone can refund or start a new subscription.

### 8. Renewed loans stay "overdue"
- Where: app/loans.py `renew_loan` (lines 13-16) and `mark_overdue`.
- Reach: staff renew an overdue loan. `due_date` moves forward but `status` stays 'overdue'. `mark_overdue` only moves open -> overdue, so nothing moves it back. `list_overdue` keeps showing it. `notices_sent` is not reset either, though the notifier query uses `due_date` so it will not email.
- Fix: set status back to 'open' on renewal when the new due date is in the future.

### 9. Trial and period expiry never change status; grace period can be skipped
- Where: app/subscriptions.py. The only job is `expire_past_due`. `is_entitled` tests `expires_at > now`.
- Reach: a trial or active subscription whose `expires_at` passes without payment stays 'trialing' or 'active' forever. Nothing moves it to past_due or canceled. Access is cut by the timestamp, but status, reports and the 14-day cancel clock say otherwise.
- Also: a subscription that goes past_due after its `expires_at` has already passed has no access during the 14-day grace, because `is_entitled` still requires `expires_at > now`.
- Severity depends on what else reads `status`. Check against the product intent.

### 10. Ticket escalation can strand a ticket
- Where: app/tickets.py `escalate_ticket` (lines 31-36), `finish_escalation` (lines 40-46), `on_event` (lines 49-52).
- Reach (a): `escalate_ticket` moves the ticket, then inserts the escalation row as a separate statement. A crash between them leaves a ticket in 'escalating' with no escalation record.
- Reach (b): the only way out of 'escalating' is the `ticket.escalation_done` event. If that event is lost, never sent, or the handler is not registered, the ticket is stuck. It cannot be resolved or closed, because both require 'open'. No timeout or manual override exists. The docstring says the handler is "registered at start-up", but nothing in app/ registers it. I could not verify that.
- Reach (c): `finish_escalation` closes the escalation rows before checking the ticket state, so an event for a ticket that is not escalating still stamps `closed_at`.
- Fix: wrap (a) in a transaction; add an admin path out of 'escalating'; guard (c) on the move result.

## Minor / Note

- Invoices (app/notifier.py `send_invoice_reminders`): every issued, overdue invoice is emailed every night with no cap or last-sent marker. Customers get a daily email until they pay. Invoices issued with NULL `due_date` are never reminded, and `issue()` does not set a due date. A reminder can also go out just after `mark_paid`, since the list is read before sending.
- app/notifier.py `send_overdue_notices`: mail is sent before the counter increments, so a crash mid-loop resends to the same members next night, and can exceed 3 in rare cases. It also reports `len(loans)` even if some sends failed.
- app/subscriptions.py `cancel`: every cancel call overwrites `revoked_at`, including on an already canceled subscription, losing the original revoke time.
- app/tickets.py `reopen_ticket` (resolved -> open) is not in the written rules. It looks intentional, but it is undocumented behaviour. `escalating` also needs a line in the rules.
- app/loans.py `close_loan` has no status guard. It is harmless because it is idempotent, but it reopens nothing and returns no success flag, so callers cannot tell a bad id from success. The same is true of `renew_loan` and the account and document functions: none return whether a row changed.
- Checked and fine: invoices (`_move` guards, void final), ticket `_move` guards and double-escalate protection, `payment_failed` only from active, `expire_past_due` using the shared `cancel`, and canceled being final in status.
