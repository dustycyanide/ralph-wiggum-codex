# Smoke Scenarios

These fixtures capture reusable live end-to-end scenarios for the Ralph Codex loop.

Each scenario includes:

- `IMPLEMENTATION_PLAN.seed.md`: the starting todo list and plan state
- `task.txt`: the exact task text for `./ralph-loop --task`
- optional helper scripts for scenario-specific setup (for example the contract mutator in `scenario-5`)

## Replay Script

Use the repo-level replay runner to reseed and execute a scenario:

```bash
./replay-smoke scenario-1
./replay-smoke scenario-5
./replay-smoke all
```

Replay runs are written under `.ralph-runs/replays/`.

## Replay Pattern

1. Copy the desired seed file over `IMPLEMENTATION_PLAN.md`.
2. Ensure any scenario-specific target files are absent before the run.
3. Run `./ralph-loop --task "$(cat smoke-scenarios/<scenario>/task.txt)" ...`.
4. Review `.ralph-runs/<run>/state.json`, `result.json`, and the repo diff.

The replay script automates steps 1-3.

## Recommended Flags

Use low reasoning for smoke runs unless the scenario proves it needs more:

```bash
./ralph-loop --task "$(cat smoke-scenarios/scenario-1/task.txt)" --loops 3 --iterations 1 --sandbox workspace-write --plan-reasoning low --build-reasoning low
```
