# Todo Scenario 2

## Goal

Verify that the planner can detect blocked work, move independent runnable work to the front of the todo list, complete it, and then return a waiting state because blocked work remains.

## Todo Requirements

### T1

- Try to read `.todo-scenario-2-input.txt`.
- If the file is missing, mark this todo blocked with `external_input`.
- Do not invent or create `.todo-scenario-2-input.txt`.
- Do not create `docs/todo-scenario-2-summary.md` while the input is missing.

### T2

Create `docs/todo-scenario-2.md` with exactly:

```md
# Todo Scenario 2

This file confirms the planner skipped blocked work and completed runnable work.
```

## Constraints

- Keep `IMPLEMENTATION_PLAN.md` as the source of truth for todo ordering and status.
- If `T1` is blocked, reorder the list so the first runnable unfinished todo is first.
- End in a waiting state if blocked work remains after runnable work is done.
