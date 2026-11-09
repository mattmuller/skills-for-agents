# The six bug shapes

Each shape lists what it is, how to search for it, and what a false alarm looks like. Check every shape against every machine.

## Contents
1. Missing reverse transition
2. Side effect not undone by the reverse
3. Stuck state
4. Timer or expiry never enforced
5. Gate missing on one path
6. Values with no database guard

## 1. Missing reverse transition

The forward move exists; the way back does not, though the rules or a sibling machine imply it.
- Search: for each transition `A -> B`, ask whether `B -> A` (or `B -> something that reaches A`) exists in code. Read the written rules for words like "later reinstate", "undo", "restore", "reopen".
- Compare siblings: if archive/restore exists for one record type, a record type with archive alone is suspect.
- False alarm: the rules say the move is final, or there is a replacement flow (a new record is created instead).

## 2. Side effect not undone by the reverse

The forward move did more than flip the field (revoked tokens, archived children, cancelled schedules, released stock, freed a name). The reverse restores only the main record.
- Search: list every statement in the forward function. For each, find its counterpart in the reverse function. A missing counterpart is the finding.
- Check children, files, cache entries, scheduled work and counters.
- False alarm: the rules say the effect is intentionally permanent (a revoked token must be reissued, not restored). Check the rules.

## 3. Stuck state

A state that cannot be left in practice.
- Search: for each state, find every code path that moves a record out of it. Then check each path is reachable: is the function called? Is the event it handles ever published? Is the route linked or authorised for anyone? Is the job scheduled?
- A function that exists and is never called does not count as an exit.
- False alarm: a terminal state the rules call final, whose entering transition is reachable and whose absence of exit is documented.

## 4. Timer or expiry never enforced

A deadline is stored but no one compares it with the clock.
- Search: every `expires_at`/`due_at`/`valid_until` column. Find where it is written, then find every read that decides access or behaviour. If no read compares it with the current time, or only a display does, it is never enforced.
- Check both enforcement styles: at read time (the check on the access path) or by a job (a sweep that changes status). A job with no schedule is no enforcement.
- False alarm: another layer enforces it (a database policy, a cache TTL). Find it before dismissing.

## 5. Gate missing on one path

Most paths check the state before acting; one does not.
- Search: for each action that should only happen in certain states (send, charge, export, display, allow access), list every code path that performs it: requests, jobs, exports, admin tools, second endpoints. Compare their state conditions line by line.
- Jobs and notifications are the usual offenders because they select by time and forget status.
- False alarm: the path is deliberately state-independent and the rules say so.

## 6. Values with no database guard

The field accepts any value.
- Search: the schema definition for the field. No CHECK, enum, lookup table or foreign key means no guard. Then look at which callers pass values from outside (an API parameter, a scanner, an import) rather than a constant.
- A boolean is a two-value guard but cannot express a third state; note when code treats it as more.
- False alarm: an application-level enum fully constrains every writer and nothing writes raw SQL. Still note it as Minor if the database would accept bad data.
