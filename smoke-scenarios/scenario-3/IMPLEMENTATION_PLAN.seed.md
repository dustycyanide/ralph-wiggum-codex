# Implementation Plan

## Goal

Run todo-driven smoke scenario 3 and confirm the planner rewrites the todo list order when a later task unblocks an earlier one.

## Scenario Notes

- The initial ordering is intentionally wrong.
- The initial `T1` depends on the initial `T2`.
- The planner should rewrite the list so the prerequisite becomes `T1` and the dependent task becomes `T2`.
- The run should end `completed` after both todos are done.

## Todo List

### T1
- Status: todo
- Title: Create `docs/todo-scenario-3-phase-2.md`
- Depends on: T2
- Validation: `diff -u docs/todo-scenario-3-phase-2.md <(printf '# Todo Scenario 3 Phase 2\n\nThis file confirms the dependent todo ran after the prerequisite todo.\n')`
- Blocker Type: none
- Blocker Detail: none

### T2
- Status: todo
- Title: Create `docs/todo-scenario-3-phase-1.md`
- Depends on: none
- Validation: `diff -u docs/todo-scenario-3-phase-1.md <(printf '# Todo Scenario 3 Phase 1\n\nThis file confirms the planner reordered the todo list.\n')`
- Blocker Type: none
- Blocker Detail: none
