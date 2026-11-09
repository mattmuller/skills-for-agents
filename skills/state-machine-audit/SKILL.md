---
name: state-machine-audit
description: Find and audit the implicit state machines in a codebase - any record whose behaviour depends on a status column, a nullable timestamp (deleted_at, archived_at, suspended_at, expires_at) or a boolean flag, with the states and transitions written down nowhere. Writes each machine down and checks it for six bug shapes that function-level tests miss. Also pins every transition with tests before a behaviour-preserving refactor. Use this whenever the user asks to audit status columns, lifecycle or workflow bugs, soft-delete or restore logic, "what states can this record be in", stuck or orphaned records, expiry or suspension logic, a pre-release bug hunt on stateful logic, or says a refactor "must not change behaviour" on code that moves records between states - even if they never say "state machine".
---

# State machine audit

A record with a `status` column, a nullable timestamp or a flag is a state machine, whether or not anyone drew it. The states and transitions live in scattered `UPDATE` statements and `if` checks. Each function can be correct alone while the edge between two states is broken, so unit tests, CI and code review pass. This skill finds those edges.

Do the work in four steps. Do not skip step 2: a finding is only as good as the written machine it was checked against.

## 1. Find every state-bearing field

Search the schema and the code, not just the schema. Look for:

- Columns named `status`, `state`, `phase`, `stage`, `kind` with a small set of values.
- Nullable timestamps used as switches: `deleted_at`, `archived_at`, `suspended_at`, `expires_at`, `closed_at`, `revoked_at`, `cancelled_at`.
- Booleans that gate behaviour: `is_active`, `revoked`, `paused`, `locked`, `on_hold`.
- Values written from code that no schema mentions (string literals in `UPDATE ... SET status`, ORM `.status =`).

List each as a candidate with the file that defines it. Read `references/finding-machines.md` for search patterns by stack (SQL, ORMs, document stores). Each candidate is either a machine to document or an exclusion with a one-line reason (for example "display-only label, nothing branches on it"). Silent exclusions are how bugs hide.

## 2. Write each machine down

For every machine, produce this block before judging anything:

```
Machine: <table.field>
States: <every value, plus "null/not null" for timestamps>
Transitions:
  <from> -> <to>  trigger: <function / route / job>  who: <role or system>
    must undo or start: <side effects this transition owns>
Entry points: <every code path that writes this field>
Readers: <every code path that branches on it>
```

Build "Entry points" and "Readers" by searching for every write and every read of the field, including jobs, event handlers, admin tools and raw SQL. The "must undo or start" line comes from the rules, not the code: read any docs, specs, comments or tests that say what the state means. Where no rule exists, say "no rule found" and infer from the sibling transition (what did the forward move change that the reverse should return?).

If a business rule and the code disagree, that is a finding. Do not quietly pick one.

## 3. Check each machine against six bug shapes

Work through every machine and every shape. Say "checked, none" when a shape does not apply; an unchecked shape is not a clean shape. Details and search tactics are in `references/bug-shapes.md`.

1. **Missing reverse transition.** A forward move has no way back although the rules, or a sibling machine, imply one (a lock with no unlock).
2. **Side effect not undone by the reverse.** The forward move touched other rows, files, tokens, caches or schedules, and the reverse only restores the main record.
3. **Stuck state.** A state with no outgoing transition that anything can actually fire. Check reachability of the trigger, not just that a function exists: a function nobody calls is no exit.
4. **Timer or expiry never enforced.** A deadline is stored and displayed but no read path or job compares it with the clock.
5. **Gate missing on one path.** Most paths check the state before acting; one path (a job, an export, a second endpoint) does not.
6. **Values with no database guard.** The field is free text or a bare boolean, with no CHECK constraint, enum or foreign key, so a typo or a bad caller creates a state nothing handles.

Terminal states are not bugs when the rules say they are final. Read the rules before calling a dead end "stuck" (a state that is final by design is documented, and its trigger is reachable).

## 4. Report each finding with reach and severity

Prove a problem before reporting it. For each finding state:

- **Where:** file and line of the missing check, transition or constraint.
- **Shape:** one of the six.
- **Reach:** can a real user or job get there? Who, by which path, how often? An unreachable path is a Note, not a defect.
- **Effect:** what goes wrong for whom, in plain words.
- **Severity:** Important (changes behaviour, money, access or personal data; fix before release), Minor (wrong but harmless), Note (observation, no action).
- **Fix:** the smallest change, with the transition it belongs to.

End with the machines that came out clean, and the exclusions from step 1. A report that lists only problems cannot be checked for coverage. Use the template in `references/report-template.md`.

Do not report more than you can show. If you are unsure a finding is reachable, say what you checked and mark it Minor or Note instead of inflating it.

## Before any refactor of this logic: pin, then refactor

"Behaviour must not change" is true only where a test would notice. When asked to refactor, simplify or clean up code that moves records between states, first follow `references/pin-then-refactor.md`:

1. List every transition from step 2.
2. Write a test per transition that asserts today's behaviour, including the side effects, even where today's behaviour looks wrong.
3. Break the code on purpose, one transition at a time, and watch the matching test fail. A pin that cannot fail pins nothing.
4. Commit the tests before touching the logic.
5. Refactor without editing those tests. If one must change, the behaviour changed: stop and tell the user.

Pin tests answer "did the refactor change it?". Tests written from the requirement answer "is it right?". Do not use one in place of the other.
