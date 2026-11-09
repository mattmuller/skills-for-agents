# State machine audit: ws1/app

Scope: read all of `schema.sql`, `docs/rules.md` and the 9 modules in `app/` (accounts, documents, invoices, loans, notifier, review_links, shipments, subscriptions, tickets). Nothing outside the app directory was read.
Checks run: full read, plus grep for every writer/caller of `on_event`, `finish_escalation`, `set_status`, restore/reinstate/expire paths. No tests or code were run. No callers (routes, schedulers, event-bus wiring) exist inside this directory, so "reach" below assumes the entry points named in the docstrings and rules exist.

## Candidates found: 14   (machines: 9, excluded: 5)

## Machines

Machine: accounts.status (+ suspended_at, api_tokens rows)
States: active, suspended (CHECK-guarded)
Transitions:
  active -> suspended  trigger: `suspend_account` (accounts.py:5)  who: support staff
    must undo or start: tokens revoked (rule: "cannot use its API tokens")
  suspended -> active  trigger: NONE found  who: support staff (rule says they can reinstate)
    must undo or start: full access back (tokens usable again), suspended_at cleared
Entry points: `suspend_account` only
Readers: `get_account_for_token` (status = 'active')

Machine: documents.archived_at / attachments.archived_at
States: document live / archived; attachment live / archived
Transitions:
  live -> archived  trigger: `archive_document`  must start: archive all live attachments with the same timestamp
  archived -> live  trigger: `restore_document`  must undo: attachments too (rule: "brings it and its attachments back")
Entry points: documents.py:7, 9, 15
Readers: `list_attachments`, `open_document_by_token`

Machine: loans.status (+ notices_sent)
States: open, overdue, closed
Transitions:
  open -> overdue  trigger: `mark_overdue` nightly job
  open/overdue -> closed  trigger: `close_loan` (any state)  must start: notices stop (rule)
  (renew) open/overdue stays same status, due_date moves
Entry points: loans.py:6, 14, 22, 29; notifier.py:15 (notices_sent)
Readers: `list_overdue`, `renew_loan`, `send_overdue_notices` (does NOT read status)

Machine: review_links.expires_at / revoked
States: valid, revoked (boolean), expired (time)
Transitions: create -> valid; valid -> revoked via `revoke_review_link`; valid -> expired by clock (rule: 7 days)
Entry points: review_links.py:10, 18
Readers: `open_document_by_token` (checks revoked, not expires_at)

Machine: tickets.status (+ escalations.closed_at)
States: new, open, escalating, resolved, closed (CHECK-guarded)
Transitions:
  new -> open  `open_ticket`
  open -> resolved  `resolve_ticket`
  resolved -> closed  `close_ticket`
  resolved -> open  `reopen_ticket`
  open -> escalating  `escalate_ticket`  must start: escalations row
  escalating -> open  `finish_escalation`  must undo: escalations.closed_at set
Entry points: tickets.py:5-46; `on_event` (tickets.py:49)
Readers: only the guarded `_move` WHERE clauses

Machine: shipments.status
States: packed, shipped, delivered (rule); column is free text
Transitions: packed -> shipped -> delivered per rule; actual: any string -> any string via `set_status`
Entry points: shipments.py:5, 10
Readers: `list_in_transit` ('shipped'), `list_awaiting_dispatch` ('packed')

Machine: subscriptions.status (+ past_due_since, expires_at, entitlements.revoked_at)
States: trialing, active, past_due, canceled (final by design)
Transitions:
  trialing/past_due -> active  `activate`  must undo: clear past_due_since, restore entitlements
  active -> past_due  `payment_failed`
  any non-canceled -> canceled  `cancel`, `expire_past_due` (nightly)  must start: revoke entitlements
Entry points: subscriptions.py:9, 18, 26, 29, 38
Readers: `is_entitled`, `expire_past_due`

Machine: invoices.status
States: draft, issued, paid, void (CHECK-guarded)
Transitions: draft->issued; issued->paid; draft/issued->void (final). All via guarded `_move`.
Entry points: invoices.py:5
Readers: `send_invoice_reminders`

## Findings

### 1. Suspended accounts can never be reinstated, and their tokens are destroyed  [Important]
- Machine: accounts.status
- Shape: 1 (missing reverse) and 2 (side effect not undone)
- Where: accounts.py:5-11. No function sets status back to 'active' or clears `suspended_at`. `suspend_account` does `DELETE FROM api_tokens` (line 11).
- Reach: any support member suspending any account (a normal staff action). Rule says staff can "later reinstate". Nothing in the app does. Every suspension is permanent unless someone edits the database by hand.
- Effect: a wrongly suspended customer cannot get access back. Even a hand fix of `status` leaves them with no tokens, so every integration they run breaks until they make new ones. "Gets back full access" is false.
- Fix: add `reinstate_account` (suspended -> active, `suspended_at = NULL`). Do not delete tokens on suspend; the `status = 'active'` check in `get_account_for_token` already blocks suspended accounts. If deletion must stay, record the tokens so reinstate can restore them.

### 2. Loan notices keep going out after the loan is closed  [Important]
- Machine: loans.status
- Shape: 5 (gate missing on one path)
- Where: notifier.py:9-12. Query is `due_date < ? AND notices_sent < ?` with no status filter.
- Reach: the nightly job. Any member who returns a book late (status 'closed', due_date in the past, notices_sent < 3) is emailed "overdue" up to three times after returning it. Happens every night for each such loan until the count reaches 3.
- Effect: members get false overdue emails. Directly breaks the rule "Closing a loan stops all notices".
- Fix: add `AND status IN ('open','overdue')` (or `status = 'overdue'`) to the query.

### 3. Review links never expire  [Important]
- Machine: review_links.expires_at
- Shape: 4 (timer never enforced)
- Where: review_links.py:22-24. `expires_at` is written at line 12 but the read query only checks `revoked = FALSE`. No job reads it either.
- Reach: anyone holding a link, indefinitely; links are meant for outside readers and get forwarded. Every link ever issued stays valid until someone revokes it by hand.
- Effect: outsiders keep access to documents after the 7-day window. This is an access/data exposure issue.
- Fix: add `AND expires_at > ?` (now) to the query.

### 4. Restoring a document leaves its attachments archived  [Important]
- Machine: documents.archived_at / attachments.archived_at
- Shape: 2 (side effect not undone)
- Where: documents.py:14-15. `archive_document` archives attachments (line 8-11), `restore_document` does not.
- Reach: any user who archives then restores a document. `list_attachments` filters `archived_at IS NULL`, so the document reappears without its files.
- Effect: attachments silently disappear from a restored document; looks like data loss. Violates the rule "brings it and its attachments back".
- Fix: in `restore_document`, also `UPDATE attachments SET archived_at = NULL WHERE document_id = ? AND archived_at = <the document's old archived_at>`. Matching the timestamp avoids un-archiving attachments that were archived separately earlier. (Archive uses one shared `now` for both, so the match works.) Also note `archive_document` on an already archived document overwrites its `archived_at` (documents.py:7); guard with `AND archived_at IS NULL`.

### 5. Shipment status accepts any text and any jump  [Important]
- Machine: shipments.status
- Shape: 6 (no guard on values) and 5 (no transition gate)
- Where: schema.sql shipments.status has no CHECK; shipments.py:8-10 writes whatever it is given with no `WHERE status = <from>`.
- Reach: the scanner API calls `set_status` with "whatever the scanner reports". A misspelling ("Shipped", "in_transit") or a stale scan out of order (delivered then a late "shipped" scan) is accepted.
- Effect: an unknown value drops the shipment out of both `list_in_transit` and `list_awaiting_dispatch`, so it is invisible. A late scan can move delivered back to shipped. Two fixes needed: a CHECK constraint, and a guarded `_move` like tickets/invoices.
- Fix: add `CHECK (status IN ('packed','shipped','delivered'))`; replace `set_status` with guarded packed->shipped and shipped->delivered moves that return a bool.

### 6. Escalated tickets can only exit through an event handler that is not wired in this code  [Minor, unverified]
- Machine: tickets.status
- Shape: 3 (stuck state)
- Where: tickets.py:40-52. 'escalating' has one exit, `finish_escalation`, called only from `on_event`. Nothing in the app registers `on_event` or emits `ticket.escalation_done` (grep found no other reference). `resolve_ticket` and `close_ticket` do not accept 'escalating'.
- Reach: unknown. The docstring says the handler is "registered at start-up", which is outside the files I was allowed to read. If it is registered and the second line emits the event, there is no bug. If not, every escalated ticket is stuck forever.
- Effect if real: tickets stuck in 'escalating' that staff cannot resolve or close.
- Fix: confirm registration and emitter exist; add a test. Consider a manual staff "hand back" path.
- Related (Minor): `finish_escalation` closes open escalation rows (line 42-45) before it checks the ticket is actually 'escalating', so a duplicate or stray event can close an escalation row while the ticket is in another state. Do the status move first, and only close the row if it succeeded. Also, if the process dies between the two statements, the order matters; run both in one transaction.

### 7. Renewed overdue loans stay 'overdue'  [Minor]
- Machine: loans.status
- Shape: 1 (missing reverse)
- Where: loans.py:12-16 and 19-24. `renew_loan` accepts 'overdue' loans and moves `due_date` forward but leaves status 'overdue'. `mark_overdue` only moves open -> overdue; nothing moves it back.
- Reach: staff renewing a loan that is already overdue.
- Effect: the staff screen (`list_overdue`) keeps showing a loan with a future due date as overdue. Harmless to members since the notifier ignores status (but see finding 2).
- Fix: in `renew_loan`, set `status = 'open'` when the new due date is in the future (and decide whether `notices_sent` resets).

### 8. `activate` and `cancel` touch entitlements even when the status change is refused  [Minor]
- Machine: subscriptions.status / entitlements.revoked_at
- Shape: 5 (gate missing on one path)
- Where: subscriptions.py:7-13 and 24-29. The status UPDATE is guarded but the entitlements UPDATE on the next line runs regardless.
- Reach: a late or duplicate payment event for a canceled subscription (billing webhook; rule says canceled is final). It clears `revoked_at` on all its entitlements. `is_entitled` still says no because it also checks status, so no live leak today. Any other reader that looks at entitlements alone would grant access. Also `activate` restores every entitlement, including any revoked for a separate reason.
- Effect: data inconsistent with the final state; latent access risk.
- Fix: run the entitlement update only if the guarded status UPDATE changed a row (check rowcount). Same in `cancel` so the first cancel timestamp is not overwritten.

### 9. Trials and paid periods have no job to end them  [Minor]
- Machine: subscriptions.status / expires_at
- Shape: 4 (timer never enforced, partially)
- Where: subscriptions.py:32-38. The only job handles past_due. `is_entitled` does compare `expires_at` (line 46), so access is correctly denied.
- Reach: any trial that is never paid, or active subscription whose period passes without a renewal event. Status stays 'trialing'/'active' forever.
- Effect: access is correct, but reports and anything that reads `status` show stale "active" accounts. No rule says what an expired trial becomes, so this may be intended. Ask the product owner.
- Related: a past_due row with `past_due_since` NULL is never canceled by `expire_past_due` (NULL < x is not true). `payment_failed` always sets it, so only reachable by manual edits; add `NOT NULL`-style CHECK (status != 'past_due' OR past_due_since IS NOT NULL).

### 10. Issued invoice with no due date never gets reminders  [Minor]
- Machine: invoices.status
- Shape: 4
- Where: schema.sql `due_date DATE` is nullable; invoices.py:9-10 `issue` does not require it; notifier.py:21 `due_date < ?` is never true for NULL.
- Reach: staff issuing a draft that has no due date.
- Effect: that invoice is never chased.
- Fix: `issue` should require `due_date IS NOT NULL`, or a CHECK (status = 'draft' OR due_date IS NOT NULL).

### 11. Reminder job runs for suspended accounts  [Note]
- Where: notifier.py:19-25. No rule on whether suspended accounts still get invoice reminders. Ask the product owner.

## Clean machines
- invoices.status: all moves go through one guarded `_move` with an expected from-state; CHECK present; void is final and no function leaves it; checked shapes 1-6, only finding 10 (nullable due_date) and 11.
- tickets.status except the escalation exit (finding 6): forward moves guarded; reopen exists; CHECK present; escalation row opened and closed in matching transitions.
- review_links.revoked: revoke exists and is honoured by the reader (expiry is finding 3).
- subscriptions.status transitions themselves (not the entitlement side effects): guarded WHERE clauses; canceled has no exit, which is final by design and its trigger (`cancel`, `expire_past_due`) is reachable; CHECK present.
- loans.status values: CHECK present; closing from any state is a benign terminal move (open/overdue/closed -> closed). No reopen exists and the rules do not ask for one.

## Exclusions
- api_tokens: rows, not a state field; covered under accounts.
- escalations.closed_at: part of the ticket machine, covered there.
- entitlements.revoked_at: side-effect field of subscriptions, covered there.
- loans.notices_sent: counter, covered under loans (limit of 3 is enforced, finding 2 is the missing status gate).
- `suspended_at` / `past_due_since`: audit timestamps that mirror their status column; nothing branches on them except `expire_past_due`.
