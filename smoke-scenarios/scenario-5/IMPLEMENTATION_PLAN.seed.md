# Implementation Plan

## Goal

Run todo-driven smoke scenario 5 and confirm the builder logs a contract issue and exits without building when the selected todo is no longer runnable.

## Scenario Notes

- The planner will select a single runnable todo.
- A test mutator will mark that todo done after planner selection and before builder execution.
- Builder should detect the contract mismatch, log a temporary Builder Contract Issue, and make no implementation artifact.
- The next planner pass should consume/remove the temporary issue and finish cleanly.

## Todo List

### T1
- Status: todo
- Title: Create `docs/todo-scenario-5.md`
- Depends on: none
- Validation: `diff -u docs/todo-scenario-5.md <(printf '# Todo Scenario 5\n\nThis file should not be created because the builder contract guard should stop work.\n')`
- Blocker Type: none
- Blocker Detail: none
