# Implementation Plan

## Goal

Run todo-driven smoke scenario 1 and confirm the loop can select and complete a single runnable todo.

## Exact Output

Create `docs/todo-scenario-1.md` with exactly:

```md
# Todo Scenario 1

This file confirms the first todo-driven smoke test.
```

## Todo List

### T1
- Status: todo
- Title: Create `docs/todo-scenario-1.md`
- Depends on: none
- Validation: `diff -u docs/todo-scenario-1.md <(printf '# Todo Scenario 1\n\nThis file confirms the first todo-driven smoke test.\n')`
- Blocker Type: none
- Blocker Detail: none
