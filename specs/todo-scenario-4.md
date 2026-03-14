# Todo Scenario 4

## Goal

Verify that the planner returns a waiting state immediately when all remaining todos are blocked by missing external input.

## Required Behavior

- `.todo-scenario-4-input-a.txt` is required for `T1`.
- `.todo-scenario-4-input-b.txt` is required for `T2`.
- If both files are missing, both todos should be marked blocked with `external_input`.
- The run should end in `waiting` without invoking builder.
