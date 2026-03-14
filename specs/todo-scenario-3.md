# Todo Scenario 3

## Goal

Verify that the planner rewrites the todo list order when an earlier task depends on a later task.

## Required Behavior

- The initial `T1` depends on the initial `T2`.
- The planner must reorder and renumber the todo list so the prerequisite task becomes `T1`.
- The dependent task must become `T2`.

## Output Files

The prerequisite todo must create `docs/todo-scenario-3-phase-1.md` with exactly:

```md
# Todo Scenario 3 Phase 1

This file confirms the planner reordered the todo list.
```

The dependent todo must create `docs/todo-scenario-3-phase-2.md` with exactly:

```md
# Todo Scenario 3 Phase 2

This file confirms the dependent todo ran after the prerequisite todo.
```
