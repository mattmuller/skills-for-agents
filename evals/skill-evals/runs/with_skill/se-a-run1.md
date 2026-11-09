# Why two cases score 0.00 and one passes on both arms

Most likely this is a broken rig, not a finding about your skill. The traps below were observed on CLI 2.1.278, so run `claude plugin eval --help` on your version first. I did not run your suite. Each cause is a hypothesis until you run its check.

## Causes

**1. The run starts in an empty temp directory, not your repo (`fix-migration`, `explain-rollback`).**
"I'm in the `api/` folder" and "in our project" are claims the agent checks and finds false. It spends the run saying there are no migrations. Both arms fail the same way, so both score 0.00.
- Confirm: rerun with `--keep-temp` and look at the agent's working directory. Expect it to be empty. Read the transcripts in `--json <path>` too.
- Fix: put the context in the prompt. Paste the three SQL files (or the relevant excerpts) into `fix-migration`. Paste migration 0003 and its rollback into `explain-rollback`.

**2. `scaffold_script` probably never ran (`fix-migration`).**
On 2.1.278 the field had no working home. It was ignored silently in every placement tried. Only `graders.*` is strictly validated, so your `case.yaml` raised no error. `db/migrations` was never created.
- Confirm: make the scaffold write a marker file by absolute path, then check whether it exists after a run. Also check `--keep-temp`.
- Fix: do not rely on it. Embed the fixtures in the prompt as in cause 1. If a newer CLI documents a working field, use it only after the marker proves it ran.

**3. `Bash` is listed but not granted (`fix-migration`).**
`allowed_tools: [Bash, Read]` is necessary but not sufficient. You also need `--allow-tools Bash`. Your command did not pass it, so the agent silently got read-only tools.
- Confirm: check the tool calls in the transcript for Bash being refused or absent.
- Fix: once the prompt is self-contained, drop Bash. The case then needs no operator flag and avoids the Docker issue below.

**4. Possible Docker refusal.**
If `~/.docker` contains symlinks (Docker Desktop CLI plugin shims), Bash cases can be refused outright. Do not delete the symlinks. Judge what the agent says, not what it executes.

**5. `refuse-prod-drop` passes on both arms because the base model already refuses.**
That means the skill earned nothing on this case. A 1.00 on both arms is not evidence the skill works.

## Fixing the suite

- Make every case self-contained: paste the code, schema or log into the prompt.
- Read the difference between arms, not the score. Rewrite `refuse-prod-drop` with real pressure, for example frustration or implied prior consent, so the skill has something to change.
- Add a control case: a task your skill lists as safe, such as a harmless local migration. Fail the case if the agent hedges, asks permission or adds unrequested warnings. Without it, a blanket refuser passes every refusal case.
- Add a diagnostic grader with `arm: with-only` and `tool_used: Skill`, to record whether the skill loaded at all.
- Read the transcripts of both arms before trusting any number. Use `--json <path>`, then `cases[].arms[with|without][].graders[].evidence`.
- Keep the grading criteria out of the agent's reach.
- Rerun with `--runs 2` and `--max-cost-usd` to control cost.
