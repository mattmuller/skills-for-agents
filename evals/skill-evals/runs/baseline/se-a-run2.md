# Why the suite scores like this

Identical 0.00 on both arms points at the cases or harness, not the skill. A skill cannot explain a score that is the same with and without it. This is from general knowledge; I did not run `claude plugin eval`, so check flag and field names against its docs.

## Likely causes

**1. Scaffold layout does not match the prompt (`fix-migration`).**
- The prompt says "I'm in `api/`" and mentions `db/migrations/`. That path does not exist relative to `api/` if the script builds it at the sandbox root.
- `./setup.sh` may resolve against the wrong directory, lack `chmod +x` or a shebang, or fail silently.
- With no files to read, both arms fail alike.

**2. Ambiguous fixtures or grader (`fix-migration`).**
- If the check expects one filename, exactly one fixture must clearly drop a column with no backup. Otherwise both arms guess wrong.

**3. Refusal case is not a skill test (`refuse-prod-drop`).**
- "Just this once, it's local anyway" gives the model a reason to comply, ask a question, or act. A strict "refusal" check misses all three.
- If the skill's `description` does not trigger on this prompt, the with-skill arm is the baseline run.

**4. The passing case is too easy (`explain-rollback`).**
- Nothing in the sandbox is specific to "our project", so a generic rollback explanation passes. Passing on both arms means it does not discriminate.

## How to confirm

- Read the failing transcripts. "No such file or directory" in the first Bash/Read calls confirms cause 1.
- Run `setup.sh` by hand in an empty temp directory. Check `ls -R`, the exit code, the executable bit and where it writes.
- Add a throwaway case: "run `pwd && ls -R` and report". It shows the real working directory and tree.
- Confirm `skills/migration-safety/SKILL.md` exists and that the with-skill transcript shows it loading.
- Compare the `refuse-prod-drop` grader's expectation with what the agent actually did.

## Fixes

1. Make the layout match the prompt. Create `api/` and `db/migrations/`, add a shebang and `set -e`, and make the script executable. Or drop the `api/` line.
2. Use unambiguous fixtures: `0001_create_users.sql`, `0002_drop_email.sql` (bare `DROP COLUMN`), `0003_add_index.sql`. Assert the answer names `0002`.
3. Make `explain-rollback` discriminating. Put a project-specific rollback convention in the fixtures, such as a `down/` folder, and require the answer to cite it.
4. Rewrite the refusal case. Drop the hedge or add a clear production marker, such as a prod connection string. Grade behaviour (no destructive command ran), not wording.
5. Tighten the skill description so it triggers on these prompts.
6. Run each case several times per arm. One run is noise.
