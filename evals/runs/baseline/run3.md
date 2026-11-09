# State-machine audit: bs3 app

Read: schema.sql, docs/rules.md, all nine files in app/. No code changed. Nothing run (no DB or tests in the directory); all findings come from reading the code against docs/rules.md.
Paths are relative to the app directory.

## High

### 1. Suspended accounts can never be reinstated (app/accounts.py:5-11)
- Rule: "Support staff can suspend an account and later reinstate it ... gets back full access."
- Problem: there is no reinstate function anywhere. `suspend_account` also DELETEs every row in `api_tokens`, so even a manual `status='active'` flip returns an account with no tokens. Suspension is destructive and one-way. `suspended_at` is never cleared either.
- Reached by: staff suspends a customer (the staff action), then needs to undo it. No code path exists; the customer must regenerate all tokens, and integrations break.
- Fix direction: keep tokens, let `get_account_for_token` (which already filters on `status='active'`) do the blocking, and add `reinstate_account`.

### 2. Overdue notices keep going out for returned (closed) loans (app/notifier.py:9-12)
- Rule: "Closing a loan stops all notices for it."
- Problem: the query is `due_date < today AND notices_sent < 3` with no `status` filter. `close_loan` sets `status='closed'` and leaves `due_date` in the past, so a returned book still gets up to 3 "overdue" emails.
- Reached by: nightly job `send_overdue_notices`, for any member who returns a late book while `notices_sent < 3`.
- Fix: add `AND status != 'closed'` (or `status = 'overdue'`).

### 3. Review links never expire (app/review_links.py:21-29)
- Rule: "open one document for seven days."
- Problem: `expires_at` is written at creation but `open_document_by_token` only checks `revoked = FALSE`. A link works forever unless someone revokes it by hand.
- Reached by: any outside reader with an old link, no special action. This is an access-control hole (outsiders reading documents after the window).
- Fix: add `AND expires_at > now`.

### 4. Shipment status accepts anything (app/shipments.py:8-10; schema.sql:61-65)
- Rule: packed -> shipped -> delivered.
- Problem: `set_status` writes whatever the scanner sends. There is no CHECK constraint, no "from" guard, no validation. A delivered shipment can go back to `packed`, `packed` can jump to `delivered`, and a typo like "shiped" is stored and then shows in neither list.
- Reached by: the scanner API, e.g. a duplicate or out-of-order scan, or a mis-scan. A shipment that regresses to `packed` reappears in `list_awaiting_dispatch` and may be dispatched twice.
- Fix: guarded transitions as in tickets/invoices (`WHERE status = <expected previous>`), plus a CHECK constraint.

### 5. Active subscriptions cannot be renewed; they silently lose access (app/subscriptions.py:7-14, 41-50)
- Rule: becomes active on first payment (nothing about later payments).
- Problem: `activate` only updates rows with `status IN ('trialing','past_due')`. A successful payment on an already `active` subscription does nothing, so `expires_at` is never extended. `is_entitled` requires `s.expires_at > now`, so an `active`, paying customer loses every feature once the first period ends. No other code extends `expires_at`.
- Reached by: any customer who pays a second period's invoice while status is `active`.
- Caveat: a renewal handler may exist outside this directory (not visible here). Confirm before treating as certain.

## Medium

### 6. Restoring a document leaves its attachments archived (app/documents.py:14-15)
- Rule: "Restoring a document brings it and its attachments back."
- Problem: `archive_document` archives attachments; `restore_document` only clears `documents.archived_at`. `list_attachments` filters on `archived_at IS NULL`, so the restored document appears with no attachments.
- Reached by: staff archive then restore a document (the normal path).
- Note: a clean fix should restore only attachments archived by that same archive action (same timestamp). Attachments archived individually earlier carry a different timestamp and should stay archived. Archive's `archived_at IS NULL` guard keeps them distinguishable.

### 7. The nightly expiry job can cancel a subscription that just paid (app/subscriptions.py:24-38)
- Problem: `expire_past_due` reads the past-due list, then calls `cancel` per row. `cancel` is guarded only by `status != 'canceled'`, not `status = 'past_due'`. If `activate` commits in between (customer pays at the moment the job runs), the subscription is `active` again and `cancel` still cancels it and revokes entitlements. Canceled is final, so a paying customer is lost with no way back.
- Reached by: payment webhook racing the nightly job. Small window, high cost.
- Fix: guard the job's update with `AND status='past_due' AND past_due_since < ?` and only revoke entitlements when the update changed a row.

### 8. Overdue loans stay "overdue" after renewal (app/loans.py:12-16, 19-23)
- Problem: `renew_loan` accepts `status IN ('open','overdue')` and only changes `due_date`. An overdue loan renewed to a future date remains `overdue`. `mark_overdue` only moves `open -> overdue`, so nothing moves it back. It stays on the staff `list_overdue` screen with a future due date.
- Reached by: a member renews a late loan.
- Fix: set `status='open'` on renewal (and consider whether `notices_sent` should reset).

### 9. Invoice reminders repeat every night with no limit (app/notifier.py:19-25)
- Problem: every night the job emails every issued invoice with `due_date < today`, with no counter or last-sent marker (loans have `notices_sent`; invoices do not). Customers get a daily reminder until paid or voided.
- Reached by: nightly job. Not a wrong state, but a missing state, and customer-facing. Severity depends on intent; no rule in docs/rules.md covers it.

## Low

### 10. `activate` and `cancel` touch entitlements even when the status change did not happen (app/subscriptions.py:13, 29)
- `activate` on a canceled subscription: the status update matches no row, but the entitlements `UPDATE ... revoked_at = NULL` runs anyway. Canceled is meant to be final, yet its entitlements are un-revoked. `is_entitled` still returns false (status check), so no access leak today, but any future code reading `entitlements` alone would grant access. It also re-grants on an `active` subscription, harmless.
- `cancel` on an already canceled subscription overwrites `revoked_at` with a later time. Harmless, but it loses the true revocation time.
- Fix: run the entitlement update only if the status update changed a row.

### 11. Escalating tickets have no way out except the second line's event (app/tickets.py:30-52)
- `escalating` can only leave via `finish_escalation` (the `ticket.escalation_done` event). If that event is lost or the second line never sends it, staff cannot resolve or close the ticket, and there is no timeout or manual override. Matches the rule as written ("hands it back when the work is done"), so this is a robustness note, not a rule violation.
- `escalate_ticket` and `finish_escalation` do two writes each with no transaction. A crash between them leaves an `escalating` ticket with no escalation row, or an escalation row closed while the ticket stays `escalating`. Recoverable by re-sending the event, since `finish_escalation` still moves the ticket.
- `finish_escalation` closes open escalation rows before checking the ticket is `escalating`; a stray or duplicate event closes the row without changing the ticket. Minor.
- `reopen_ticket` (resolved -> open) is not in the written rules. Possibly intended; confirm with the product owner.

### 12. Smaller observations
- `suspend_account` on an already suspended account overwrites `suspended_at`.
- Trialing subscriptions are never moved on trial end or on a failed payment (`payment_failed` only handles `active`). Entitlement is protected only by `expires_at`. Rules are silent here.
- Invoices: no problems found in the transitions. `_move` guards each step, void is final from draft/issued. Draft invoices with NULL `due_date` are never reminded once issued; low.
- `close_loan` is unguarded (closes from any state, including already closed). Harmless.
- Ticket transitions are all guarded and match the rules, apart from the points above.

## Summary
Guarded-transition helpers (tickets, invoices) are sound. Problems cluster where a state change is split across tables or jobs without being kept consistent: accounts/tokens, loans/notifier, documents/attachments, subscriptions/entitlements. The other cluster is a rule written in docs but not enforced in the query (review link expiry, shipments).
