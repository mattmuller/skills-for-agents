# Pin, then refactor

Use before any change described as "behaviour must not change" on logic that moves records between states, handles money, access, personal data or limits.

## Why

A quality pass or refactor usually runs only the tests near the files it touched. A transition with no test can change silently. "Behaviour must not change" is true only where a test would notice.

## Steps

1. **List the transitions.** Use the machine block from the audit. One row per transition, including the side effects it owns.
2. **Write a pin test per transition.** Assert today's behaviour: the new state, the side effects, and what is refused. If today's behaviour looks wrong, pin it anyway and record the oddity as a finding. A pin records what is, not what should be.
3. **Prove each pin can fail.** Break the code on purpose, one transition at a time (remove the side effect, swap a status, drop a guard), run the test, and confirm it fails. Restore the code. For a stronger check, run a mutation testing tool on the file that holds the logic and read the surviving mutants in the transition functions only.
4. **Commit the pins alone,** before the refactor, so the diff shows they were written against the old code.
5. **Refactor with the pin files frozen.** Check at the end that the pin test files have no diff (`git diff --stat <pin-commit> -- <test files>` is empty).
6. **If a pin must change, stop.** The behaviour changed. Tell the user which transition and why, and let them decide.

## Two kinds of test

- Pin tests answer "did the refactor change it?". Written from the old code.
- Spec tests answer "is it right?". Written from the requirement, ideally by someone who has not read the code.

A change with neither is not ready. Do not let one stand in for the other.
