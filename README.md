# Ralph Codex Loop

This repository contains a Ralph-style autonomous loop runner built on the Codex CLI.

Defaults are:

- planner: `gpt-5.3-codex` with `model_reasoning_effort="high"`
- builder: `gpt-5.2-codex` with `model_reasoning_effort="high"`

It uses `codex exec` (non-interactive mode) and schema-constrained JSON outputs so the loop can decide on its own when to stop.

## Requirements

- Python 3.10+
- Codex CLI installed (`codex --version`)
- Codex authenticated (`codex login` if needed)

## Important note about `exec-c`

`exec-c` is not a Codex command. The correct command is:

```bash
codex exec
```

The `-c` flag is for config overrides (for example `-c 'model_reasoning_effort="high"'`).

## Files in this setup

- `ralph-loop` - shell entrypoint
- `ralph/codex_loop.py` - loop orchestrator
- `ralph/schemas/plan.schema.json` - planner response schema
- `ralph/schemas/build.schema.json` - builder response schema
- `docs/ralph-research.md` - research notes and source links
- `AGENTS.md` - operational guidance loaded by Codex during loops
- `IMPLEMENTATION_PLAN.md` - persistent task state across loop iterations
- `specs/README.md` - where to place project spec files

## Quick start

```bash
chmod +x ./ralph-loop
./ralph-loop --task "Build a tiny CLI that prints hello" --loops 3 --iterations 4
```

Positional task input also works:

```bash
./ralph-loop Build a tiny CLI that prints hello --loops 3 --iterations 4
```

## Useful examples

Default routing (planner 5.3 high, builder 5.2 high):

```bash
./ralph-loop --task "<project idea>" --loops 6 --iterations 6
```

Explicit model and reasoning selection:

```bash
./ralph-loop \
  --task "<project idea>" \
  --plan-model gpt-5.3-codex \
  --plan-reasoning high \
  --build-model gpt-5.2-codex \
  --build-reasoning high
```

Run in background:

```bash
./ralph-loop --task "<project idea>" --loops 8 --iterations 8 --background
```

The background command prints run directory, log file, and PID.

## Loop controls

- `--loops`: max planner loops
- `--iterations`: max builder iterations for each planner loop
- `--blocked-policy`: `stop`, `next-loop`, or `continue`
- `--sandbox`: `read-only`, `workspace-write`, or `danger-full-access`
- `--plan-config KEY=VALUE`: extra `-c` for planner calls
- `--build-config KEY=VALUE`: extra `-c` for builder calls
- `--search`: enable live web search during codex exec

## Autonomous stopping behavior

The loop exits automatically when either phase returns completion:

- planner can set `done=true` if goal is already complete
- builder can set `status="completed"` or `done=true`

This is the added behavior versus basic infinite-loop Ralph scripts.

## Run artifacts

Each run writes to `.ralph-runs/run-<timestamp>/`:

- `task.txt`
- `state.json`
- `result.json`
- per-step logs and JSON outputs (`loop-*-planner.log`, `loop-*-builder.log`, etc.)

This gives you full traceability for every loop and iteration.
