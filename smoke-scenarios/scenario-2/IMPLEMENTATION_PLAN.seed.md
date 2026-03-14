# Implementation Plan

## Goal

Run todo-driven smoke scenario 2 and confirm the planner can skip blocked work, complete independent work, and then wait on the remaining blocker.

## Scenario Notes

- `T1` requires a missing external input file and should become blocked.
- `T2` is independent and should become the active todo after reordering.
- The run should end in `waiting` after `T2` is complete because `T1` still needs external input.

## Todo List

### T1
- Status: todo
- Title: Summarize `.todo-scenario-2-input.txt` into `docs/todo-scenario-2-summary.md`
- Depends on: none
- Validation: `test -f docs/todo-scenario-2-summary.md`
- Blocker Type: none
- Blocker Detail: none

### T2
- Status: todo
- Title: Create `docs/todo-scenario-2.md`
- Depends on: none
- Validation: `diff -u docs/todo-scenario-2.md <(printf '# Todo Scenario 2\n\nThis file confirms the planner skipped blocked work and completed runnable work.\n')`
- Blocker Type: none
- Blocker Detail: none
