# Why two cases score 0.00 on both arms, and one passes on both

Read the difference between arms, not the score. Equal scores on both arms mean the skill changed nothing. Here the rig is probably broken. Caveat: the traps below were observed on CLI 2.1.278, so check `claude plugin eval --help` on your version first.

## Likely causes

**1. `fix-migration` is scored against an empty directory (most likely).**
The run gets a fresh, empty temp folder, not your repo. "I'm in the `api/` folder, look at `db/migrations/`" is a claim the agent checks, finds false, and reports. Both arms fail the same way, so you get 0.00 and 0.00.
- Confirm: rerun with `--keep-temp` and list the folder. Read the agent's answer in `--json <path>` under `cases[].arms[with|without][].graders[].evidence`.
- Fix: paste the three migration files straight into `prompt.md`.

**2. `scaffold_script` silently did nothing.**
It did not run in any placement tried (top level of `case.yaml`, `execution:`, `setup:`, a `scaffold.sh` beside the case). Only `graders.*` is strictly validated, so an unknown key is ignored without complaint. Your fixtures never existed.
- Confirm: make `setup.sh` write a marker file by absolute path (`touch /tmp/scaffold-ran`). If it is missing after a run, the scaffold never ran.
- Fix: stop depending on it. Inline the fixtures in the prompt.

**3. `Bash` is gated, and may be refused outright.**
`allowed_tools: [Bash, Read]` is necessary but not sufficient. You also need `--allow-tools 'Bash'` on the command line. You did not pass it, so the agent got read-only tools. Separately, Bash cases can be refused entirely if `~/.docker` contains a symlink (Docker Desktop's `cli-plugins` shims do this).
- Confirm: look for a refusal message or missing tool calls in the transcript. Check `ls -l ~/.docker/cli-plugins`.
- Fix: pass `--allow-tools`. Better, drop Bash. Pasted SQL needs only reading. Do not delete the symlinks.

**4. Why one case passes on both arms.**
`refuse-prod-drop` needs no repo and no tools, so it works in an empty directory. A pass on both arms means the base model already refuses. That is a skill that earned nothing on that case, not a success. `explain-rollback` has the same empty-repo problem as case 1, which is probably your second 0.00. I cannot see its prompt, so that is an inference.

## Fixing the suite

- Make every case self-contained: paste code, schema or logs into the prompt.
- Run with `claude plugin eval skills/migration-safety --no-publish -j 4 --allow-tools 'Bash'`, only if a case truly needs Bash.
- Add a control case: a safe task the skill's own text allows (for example, dropping a column that has a backup step). Fail it if the agent hedges, asks permission or adds unrequested warnings. Otherwise a blanket refuser passes every refusal case.
- Strengthen the pressure in `refuse-prod-drop`. "Just this once, it's local anyway" is a good start. Add frustration or implied prior consent.
- Add a diagnostic grader with `tool_used: Skill` and `arm: with-only`. It records whether the skill loaded at all, without scoring.
- Keep graders in `graders/criteria.md`, away from the agent's working directory.
- Read the transcripts of both arms before quoting any number. Check that the passing answers were actually better.
- Budget: 3 cases at defaults is about 18 agent runs. Use `--runs 2` and `--max-cost-usd` as a ceiling.
