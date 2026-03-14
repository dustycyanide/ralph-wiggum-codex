# Todo Scenario 5

## Goal

Verify that builder logs a contract issue and exits without implementation when the selected todo is no longer runnable by the time builder starts.

## Required Behavior

- Planner initially selects `T1`.
- A test mutator marks `T1` done before builder begins.
- Builder must detect that there is no longer a runnable todo matching the planner selection.
- Builder must not create `docs/todo-scenario-5.md`.
- Builder must log a temporary contract issue for planner consumption.
- Planner must remove that temporary contract issue on the next pass and then finish cleanly.
