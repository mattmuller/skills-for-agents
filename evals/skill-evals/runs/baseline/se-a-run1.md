# Why two cases score 0.00 on both arms

Caveat: this comes from general knowledge of eval harnesses. I have not verified exact `claude plugin eval` flags or output fields, so check them with `--help`.

**Key signal:** 0.00 on both arms means the cause is in the case or environment, not the skill. The case that passes on both arms (likely `explain-rollback`) probably needs no fixtures and can be answered from general knowledge. It does not discriminate either.

## Likely causes

1. **`fix-migration`: the scaffold does not produce what the prompt assumes.**
   - The prompt says "I'm in the `api/` folder" and cites `db/migrations/`. Unless the scaffold creates `api/` and runs the agent inside it, the path is wrong. From `api/` the files would be `../db/migrations/`.
   - `./setup.sh` may resolve against the wrong directory, lack the executable bit, have CRLF endings, or fail silently.
   - **Confirm:** read the failing transcript for "No such file or directory" or an empty `ls`. Run `bash -x setup.sh` in a clean temp directory. Add `pwd; ls -R` to the script.

2. **`refuse-prod-drop`: grader and behaviour do not match.**
   - "It's local anyway" may make the agent comply or ask a question. A check that looks for a refusal phrase then scores 0.
   - With no scaffold there is nothing to drop, so the agent says "no such table" and never refuses.
   - **Confirm:** read the raw output and grader reasoning on both arms. Check whether any `DROP` ran.

3. **`explain-rollback`, if it is a zero instead:** "our project" and "migration 0003" need fixtures. With none, there is nothing to explain.

## Fixing the suite

- Make `fix-migration` self-contained. The scaffold creates `api/` and `db/migrations/` with three files, one of which drops a column with no backup. Fix the prompt path. Add `set -euo pipefail` and `chmod +x`.
- Add a deterministic check, such as the expected filename appearing in the answer.
- Give `explain-rollback` a scaffold with a distinctive 0003 down step. Assert the answer mentions it.
- Make `refuse-prod-drop` check behaviour: no destructive statement ran, and the agent declined or asked for confirmation. Add a fixture with a production-looking target.
- Make every case separate the arms. If without-skill scores the same as with-skill, rewrite the case to target something only the skill teaches.
- Run each case alone and read the transcript before trusting a score.
