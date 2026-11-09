# State-transition audit: bs2/app

Scope: all of `app/*.py`, `schema.sql`, `docs/rules.md`. No code was changed or run; findings come from reading only.

## High

### 1. Overdue notices go out for closed loans (`app/notifier.py:9-15`)
- Query is `WHERE due_date < ? AND notices_sent < ?`. It never looks at `status`.
- Rule broken: "Closing a loan stops all notices for it."
- Reached by: the nightly `send_overdue_notices` job. A member returns a book (`close_loan` sets `closed`), and still gets up to 3 notices.
- It also sends to `open` loans that `mark_overdue` has not yet flipped, so the result depends on job order.
- Fix: add `AND status IN ('open','overdue')` (or `status = 'overdue'`).

### 2. A suspended account can never be reinstated, and reinstating could not restore access (`app/accounts.py:5-11`)
- There is no reinstate function at all. Suspension is one-way in code.
- `suspend_account` also deletes every row in `api_tokens`. Even if staff flip `status` back by hand, the tokens are gone, so "gets back full access" is false.
- Reached by: staff click "suspend". Nothing can undo it short of manual SQL and customers re-issuing tokens.
- Fix: add `reinstate_account` (status to `active`, clear `suspended_at`). Keep tokens and let `get_account_for_token` refuse suspended accounts (it already does), or record which tokens were revoked.

### 3. Review links never expire (`app/review_links.py:21-29`)
- `open_document_by_token` checks `revoked = FALSE` but never compares `expires_at` to now.
- Rule broken: "lets an outside reader open one document for seven days."
- Reached by: any outside reader holding an old URL. It works forever unless someone revokes it. This is an access-control hole.
- Fix: add `AND expires_at > ?` with the current time.

### 4. Renewal payments do not extend an active subscription (`app/subscriptions.py:7-13`)
- `activate` only matches `status IN ('trialing','past_due')`. A payment on an already `active` subscription changes nothing, so `expires_at` is never moved forward.
- `is_entitled` requires `expires_at > now`. A paying active customer loses entitlements when the first period ends.
- Reached by: any recurring payment webhook calling `activate` on an active sub.
- Related: nothing moves a subscription at expiry. No job turns `active`/`trialing` with a passed `expires_at` into `past_due` (the only nightly job handles `past_due`). Trials that run out stay `trialing` indefinitely.
- Fix: handle renewal on `active` (extend `expires_at`), and add an expiry job for trial/active.

## Medium

### 5. Restoring a document does not restore its attachments (`app/documents.py:14-16`)
- `restore_document` only clears the document's `archived_at`. `archive_document` archived the attachments too.
- Rule broken: "Restoring a document brings it and its attachments back."
- Reached by: any user restoring an archived document. It reappears with no attachments (`list_attachments` filters them out).
- Care needed in the fix: attachments archived on their own earlier should stay archived. Match on the same `archived_at` timestamp as the document, or store an archive reason.

### 6. `activate` and `cancel` touch entitlements without checking the subscription state (`app/subscriptions.py:7-13, 24-29`)
- `activate` runs the `UPDATE entitlements ... revoked_at = NULL` unconditionally, even when the guarded status update matched no row. Calling it on a `canceled` subscription un-revokes its entitlements while the status stays `canceled`. "Canceled is final" is then violated in the data. `is_entitled` still checks status, so access is held back only by that second check.
- `cancel` rewrites `revoked_at` with a fresh time every call, even on an already canceled subscription.
- Reached by: late or duplicate payment webhooks, and repeated cancel calls.
- Fix: act on entitlements only if the status update changed a row (check rowcount).

### 7. Shipment status is unvalidated (`app/shipments.py:8-10`, `schema.sql` shipments)
- `set_status` writes whatever the scanner API sends. No allowed-from check, no CHECK constraint on the column (every other table has one).
- Reached by: the scanner API. A duplicate or out-of-order scan sets `delivered` back to `packed` or `shipped`. A typo creates a status no list query shows. `packed` can jump straight to `delivered`.
- Rule: packed to shipped to delivered only.
- Fix: guarded `UPDATE ... WHERE status = <previous>` per step, like `invoices._move`, plus a CHECK.

### 8. Renewing an overdue loan leaves it `overdue` (`app/loans.py:12-24`)
- `renew_loan` accepts `overdue` and moves `due_date`, but never sets the status back to `open`. `mark_overdue` only looks at `open`.
- Reached by: staff or member renewing a late loan. It stays on the staff overdue list (`list_overdue`) though its new due date is in the future.
- Fix: set `status = 'open'` when the new due date is after today, or rename the state to match.

## Low

### 9. `close_loan` is unconditional (`app/loans.py:27-29`)
- No `WHERE status != 'closed'`, no check the loan exists. Harmless today, but it hides a double-return and gives no signal. Other modules return a bool.

### 10. Ticket escalation is not atomic and can stick (`app/tickets.py:30-52`)
- `escalate_ticket` moves the status, then inserts the escalation row in a separate statement. A failure between them leaves a ticket `escalating` with no escalation record.
- `finish_escalation` closes the escalation row before it checks the ticket is `escalating`. A stray or replayed `ticket.escalation_done` event closes an escalation row for a ticket in another state. `on_event` ignores the return value.
- Nothing times out an escalation. If the second line never sends the event, the ticket stays `escalating`, where `resolve_ticket` and `close_ticket` cannot reach it.
- Fix: one transaction, and do the status move first and the row update only if it returned True.

### 11. Duplicate overdue notices after a crash (`app/notifier.py:14-15`)
- Mail is sent, then the counter is incremented, with no transaction. A crash or error in between resends the notice on the next run and can exceed the cap of 3.

### 12. Invoice reminders have no limit (`app/notifier.py:19-25`)
- Every night, every issued invoice past its due date gets a reminder, forever. No rule here states a cap, so this is a product question. Invoices with `due_date` NULL are skipped silently (fine).

### 13. `suspend_account` is not guarded (`app/accounts.py:5-11`)
- Re-suspending overwrites `suspended_at`. `actor` is accepted and never recorded.

## Checked and looks correct
- `invoices.py`: every move is a guarded UPDATE; void is final.
- Ticket main path new, open, resolved, closed, and `reopen_ticket` resolved to open (not in the written rules; confirm it is intended).
- `expire_past_due`: uses the 14-day grace period correctly. `payment_failed` only applies to `active` (a failing trial is not a case in the rules).
