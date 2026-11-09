# Results, iteration 1 (9 Nov 2026)

Model: Sonnet 5.5, three runs per arm, same prompt, fresh agent each. Arm A read the skill first. Arm B got no skill. Each run saw only a copy of `sample-app/`. Findings are in `runs/`. I graded by hand against `answer-key.json`.

| Planted bug | With skill | Baseline |
|---|---|---|
| Missing reverse transition | 3/3 | 3/3 |
| Side effect not undone by the reverse | 3/3 | 3/3 |
| Stuck state | 3/3 | 1/3 (strict), 3/3 (lenient) |
| Timer never enforced | 3/3 | 3/3 |
| Gate missing on one path | 3/3 | 3/3 |
| No database guard | 3/3 | 3/3 |

Strict means the run said nothing registers the handler or publishes the event. Both other baseline runs saw the ticket could stay in "escalating" if the event never came, but one called it a robustness note that "matches the rule as written", and the other called it a possibility. Lenient counts those.

Decoys. No run called a state that is final by design (canceled subscription, void invoice) a bug. Every run, in both arms, did report issues in the two decoys: a paid renewal on an active subscription never extends its expiry, a late payment event re-grants entitlements on a canceled subscription, an issued invoice with no due date is never reminded, invoice reminders have no cap. Those are real gaps in my decoy code, not false alarms, so the decoys were not fully clean. I did not count them as false positives, and I have not fixed them, so the numbers above stand as measured.

What this does and does not show.
- On a small app a plain agent already finds five of the six shapes every time. The skill's measurable gain here is on the stuck state.
- The skill text names generic checks (a function nobody calls is no exit) that overlap with the planted stuck state, so that row is the least independent. The bugs were written by the same person who wrote the skill.
- Three runs per arm is a small sample. The with-skill reports were longer, listed the machines first and ended with clean machines and exclusions; the baselines did not.
- Not measured: larger codebases, other languages, the pin-then-refactor step.
