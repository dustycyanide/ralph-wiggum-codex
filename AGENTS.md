## Brief Overview

Ralph is not just a loop that codes. It is a funnel with three phases, two prompts, and one loop:

1. Define requirements (`specs/*`).
2. Planning mode (gap analysis, update `IMPLEMENTATION_PLAN.md`, no implementation).
3. Building mode (implement from plan, run checks, keep plan current).

This repo runs that pattern with `codex exec`: planner defaults to `gpt-5.3-codex` (high reasoning), builder defaults to `gpt-5.2-codex` (high reasoning). The loop keeps persistent state on disk and uses fresh context each iteration.

## Directory Structure

```
.
├── AGENTS.md
├── IMPLEMENTATION_PLAN.md
├── README.md
├── docs/
│   └── ralph-research.md
├── ralph-loop
├── ralph/
│   ├── codex_loop.py
│   └── schemas/
│       ├── plan.schema.json
│       └── build.schema.json
├── specs/
│   └── README.md
└── .ralph-runs/
```

## Steps: Planning and Building

1. Write or update requirements in `specs/*`.
2. Run planning pass:
   - `./ralph-loop --task "Plan only: compare specs to code and update IMPLEMENTATION_PLAN.md; do not implement." --loops 1 --iterations 1 --sandbox workspace-write`
3. Run building loop:
   - `./ralph-loop --task "Implement the project from specs and IMPLEMENTATION_PLAN.md" --loops <n> --iterations <n> --sandbox workspace-write`
