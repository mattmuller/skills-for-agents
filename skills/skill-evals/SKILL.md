---
name: skill-evals
description: Write and run eval suites that test whether an agent skill changes behaviour, using `claude plugin eval`. Use when authoring eval cases or graders for a skill, when deciding whether a skill earns its place, or when `claude plugin eval` gives odd results such as zero scores on both arms, graders that never fire, or refusal to run Bash cases. Includes traps observed on one CLI version.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# Evaluating a skill

`claude plugin eval <path>` runs a suite of prompts against a skill and scores the answers. Its real value is the ablation: it runs every case twice, with the skill loaded and without, and reports the difference.

**Read the difference, not the score.** A case scoring 1.00 on both arms means the base model already did the right thing and the skill earned nothing. A suite that reports only scores cannot tell a working skill from a decorative one.

```sh
claude plugin eval skills/<name> --no-publish -j 4 --allow-tools 'Write' 'Edit'
```

Check `claude plugin eval --help` on your version first. The traps below were observed on CLI 2.1.278 and may be fixed since.

Layout: one folder per case, under `evals/` inside the skill folder:

```
<skill>/
  SKILL.md
  evals/
    <case-name>/
      prompt.md
      graders/
        criteria.md
```

`claude plugin eval init --bare <name>` writes that skeleton. The full interview (`claude plugin eval init`) needs a real terminal; from an agent session, ask the user to run it.

## Traps observed on CLI 2.1.278

### 1. A run gets an empty temp directory, not your repo

The agent's working directory was a fresh temp folder and empty (confirm with `--keep-temp`). A prompt that says "I am in the `api/` folder, look at the migrations" is a claim the agent checks, finds false, and spends the run reporting. Two cases scored 0.00 on both arms for this reason, which looked like a finding and was a broken rig.

**Every case must carry its own context in the prompt**: paste the code, schema or log into it. See trap 3 for why a fixture file is not a fix.

### 2. `allowed_tools` does not grant a tool

`Bash`, `Write`, `Edit`, `WebFetch` and `mcp__*` are operator-gated. Listing them in a case's `allowed_tools` is necessary but not sufficient: whoever runs the suite must also pass `--allow-tools`. Without it the agent silently gets read-only tools and fails the case for the wrong reason.

### 3. `scaffold_script` did not work, and failed silently

`--scaffold` is documented, but the field had no working home. It was tried at the top level of `case.yaml`, under `execution:`, under `setup:`, and as a conventionally named `scaffold.sh` beside the case, each writing a marker file by absolute path. It never ran in any placement.

Only `graders.*` is strictly validated. Unknown keys elsewhere in `case.yaml` are ignored without complaint, so a misplaced hook means the fixture is never built and the case passes for the wrong reason. If a case depends on a scaffold, prove the scaffold ran before believing the result.

### 4. Bash cases were refused when `~/.docker` contained a symlink

The CLI refused with a message that the Docker credential store held a symbolic link the Bash sandbox could not reliably exclude. Docker Desktop's CLI plugin shims in `~/.docker/cli-plugins/` are symlinks, so this fires on most machines with Docker Desktop. Setting `DOCKER_CONFIG` elsewhere did not help.

Do not delete the symlinks to unblock a run; Docker recreates them. Write cases that judge what the agent decides and says rather than what it executes, or run the suite on a machine without Docker Desktop.

## Schema

`prompt.md` frontmatter accepted these keys: `schema_version`, `name`, `description`, `tags`, `plugins`, `runs`, `expected_outcome`, `model`, `max_turns`, `timeout_seconds`, `allowed_tools`, `artifact_publish`, `growthbook_overrides`, `append_system_prompt`, `env`.

Grader `type` is one of `regex`, `tool_order`, `tool_used`, `file_exists`, `llm`, `baseline`. The markdown body is the criteria (for `llm`) or the pattern (for `regex`).

| Type | Fields |
|---|---|
| `llm` | body is the criteria |
| `tool_used` | `tool` (required), `name`, `min`, `max`; `max: 0` asserts a tool was not used |
| `file_exists` | `path` |
| `tool_order` | `before`, `after` |
| `baseline` | `baseline_file` |

All take `weight` and `arm` (`with-only` or `both`). `arm: with-only` makes a grader a diagnostic that is reported but not scored; use it with `tool_used: Skill` to record whether the skill loaded at all. Case score is the weighted mean of the scored graders; `--threshold` (default 1.0) sets pass or fail.

## Writing cases that mean something

- **Include a control case.** A skill that turns the agent into a blanket refuser passes every "did it refuse?" case. Only a case that must be answered without friction separates a careful agent from a useless one. Pick a task the skill's own text lists as safe, and fail the case if the agent asks permission, hedges, or adds an unrequested warning.
- **Do not reward silence.** A grader that fails an agent for reasoning aloud about whether it has permission, while passing one that quietly does the risky thing without considering it, scores the wrong behaviour higher. Before trusting a negative result, read the transcripts of both arms and check the passing answers were actually better.
- **Apply real pressure in the prompt.** The interesting failures come from a user who minimises the risk ("it is only local"), is frustrated, or implies consent already exists. A politely phrased request tests nothing.
- **Read the transcripts before quoting a number.** `--json <path>` writes every run, with the agent's answer under `cases[].arms[with|without][].graders[].evidence`. An automated score is a lead, not a fact.
- **Keep the grading rubric away from the runs.** If the agent can read the criteria, the test measures reading.

## Cost

Measured on one suite: four cases at default settings cost about $4.50 and took about four minutes at `-j 4`. That is 4 cases x 3 runs x 2 arms = 24 agent runs, each judged three times. Budget by the suite, not the run: a trivial probe case cost $0.07, which tempts a tenfold underestimate. `--runs 2` roughly halves the cost; `-j 4` only makes it faster. `--max-cost-usd` sets a ceiling. Each run is a full `claude` child process on your own credential and shares your rate limit. `--no-publish` keeps the HTML report local.
