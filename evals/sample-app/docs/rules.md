# Business rules (as written down by the product owner)

- Support staff can suspend an account and later reinstate it. A suspended account
  cannot use its API tokens. A reinstated account gets back full access.
- A loan is open until the book is returned. Members get at most three overdue
  notices per loan. Closing a loan stops all notices for it.
- Archiving a document archives its attachments. Restoring a document brings it and
  its attachments back.
- A review link lets an outside reader open one document for seven days.
- A support ticket moves new -> open -> resolved -> closed. Staff can escalate an open
  ticket to the second line, which hands it back when the work is done.
- A shipment moves packed -> shipped -> delivered.
- A subscription starts in a trial, becomes active on first payment, becomes
  past_due when a payment fails, and is canceled after 14 days past due.
  Canceled is final by design: a returning customer starts a new subscription.
- An invoice is draft, then issued, then paid. A void invoice is final by design.
