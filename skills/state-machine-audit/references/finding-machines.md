# Finding implicit state machines

Search by what the field does, not only by its name. Run every search over schema, migrations, application code, jobs, scripts and admin tools.

## Contents
- Schema-side searches
- Code-side searches
- What to exclude, and how to say so
- Completeness check

## Schema-side searches

- Columns named `status`, `state`, `phase`, `stage`, `step`, `kind`, `mode`.
- Nullable timestamps: `*_at` columns that start NULL (`deleted_at`, `archived_at`, `suspended_at`, `closed_at`, `revoked_at`, `expires_at`, `paused_at`).
- Boolean columns that gate behaviour: `is_*`, `*_enabled`, `revoked`, `locked`, `paused`, `on_hold`.
- `CHECK (col IN (...))` constraints and enum types: they list the declared states.
- Columns with no constraint at all that look like the above. Those are shape 6 candidates.

## Code-side searches

- `SET status =`, `SET state =`, `.status =`, `status:` in update calls, string comparisons such as `== "active"` or `WHERE status IN (...)`.
- Literals used with a field but absent from its constraint (a state the schema does not know).
- `NOW()` / `datetime.now()` stored into a `*_at` column, and `IS NULL` / `IS NOT NULL` tests on it.
- Scheduled jobs, queue consumers and event handlers: they write states without a user action, so they are easy to miss.
- Raw SQL in admin scripts and migrations that move rows between states.

## What to exclude, and how to say so

Exclude a field only with a reason: display-only label, audit timestamp that nothing reads, value set once at creation and never branched on. Record the exclusion in the report. If a "display-only" field is read by any branch, it is a machine.

## Completeness check

Before step 2, count the candidates and the machines plus exclusions. The two numbers must match. Then pick one machine at random and confirm you listed every function that writes it (grep the field name across the whole repo once more). Missed entry points are the most common cause of missed bugs.
