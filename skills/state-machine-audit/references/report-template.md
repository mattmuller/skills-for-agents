# Report template

Use this layout. Keep it to what you checked.

```
# State machine audit: <project or path>

Scope: <directories read, what was skipped>
Checks run: <searches, tests, anything executed; say "not run" for what was not>

## Candidates found: <n>   (machines: <m>, excluded: <e>)

## Machines
<one block per machine, as in step 2 of SKILL.md>

## Findings
### <number>. <short title>  [Important | Minor | Note]
- Machine: <table.field>
- Shape: <one of the six>
- Where: <file:line>
- Reach: <who can get there, by which path, how often>
- Effect: <what goes wrong, in plain words>
- Fix: <smallest change>

## Clean machines
<machine: shapes checked, none found>

## Exclusions
<field: reason>
```

Order findings by severity. Do not merge two findings that need two fixes.
