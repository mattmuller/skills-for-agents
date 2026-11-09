-- Schema for the sample app (a small back office: loans, accounts, documents,
-- tickets, shipments, subscriptions, invoices).

CREATE TABLE accounts (
  id            INTEGER PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  status        TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended')),
  suspended_at  TIMESTAMP
);

CREATE TABLE api_tokens (
  id          INTEGER PRIMARY KEY,
  account_id  INTEGER NOT NULL REFERENCES accounts(id),
  token       TEXT NOT NULL
);

CREATE TABLE loans (
  id          INTEGER PRIMARY KEY,
  member_id   INTEGER NOT NULL,
  book_id     INTEGER NOT NULL,
  due_date    DATE NOT NULL,
  status      TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'overdue', 'closed')),
  notices_sent INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE documents (
  id           INTEGER PRIMARY KEY,
  title        TEXT NOT NULL,
  archived_at  TIMESTAMP
);

CREATE TABLE attachments (
  id           INTEGER PRIMARY KEY,
  document_id  INTEGER NOT NULL REFERENCES documents(id),
  filename     TEXT NOT NULL,
  archived_at  TIMESTAMP
);

CREATE TABLE review_links (
  id           INTEGER PRIMARY KEY,
  document_id  INTEGER NOT NULL REFERENCES documents(id),
  token        TEXT NOT NULL UNIQUE,
  expires_at   TIMESTAMP NOT NULL,
  revoked      BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE tickets (
  id        INTEGER PRIMARY KEY,
  subject   TEXT NOT NULL,
  status    TEXT NOT NULL DEFAULT 'new'
            CHECK (status IN ('new', 'open', 'escalating', 'resolved', 'closed'))
);

CREATE TABLE escalations (
  id         INTEGER PRIMARY KEY,
  ticket_id  INTEGER NOT NULL REFERENCES tickets(id),
  opened_at  TIMESTAMP NOT NULL,
  closed_at  TIMESTAMP
);

CREATE TABLE shipments (
  id        INTEGER PRIMARY KEY,
  order_ref TEXT NOT NULL,
  status    TEXT NOT NULL DEFAULT 'packed'
);

CREATE TABLE subscriptions (
  id            INTEGER PRIMARY KEY,
  account_id    INTEGER NOT NULL REFERENCES accounts(id),
  status        TEXT NOT NULL DEFAULT 'trialing'
                CHECK (status IN ('trialing', 'active', 'past_due', 'canceled')),
  expires_at    TIMESTAMP NOT NULL,
  past_due_since TIMESTAMP
);

CREATE TABLE entitlements (
  id               INTEGER PRIMARY KEY,
  subscription_id  INTEGER NOT NULL REFERENCES subscriptions(id),
  feature          TEXT NOT NULL,
  revoked_at       TIMESTAMP
);

CREATE TABLE invoices (
  id        INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES accounts(id),
  status    TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'issued', 'paid', 'void')),
  due_date  DATE
);
