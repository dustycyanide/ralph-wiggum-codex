# Implementation Plan

## Goal

Run todo-driven smoke scenario 4 and confirm the planner returns waiting immediately when all remaining todos are blocked on missing external input.

## Scenario Notes

- Both todos require missing external input.
- No runnable todo exists at the start of the run.
- The planner should mark blocked metadata and return `waiting` without invoking builder.

## Todo List

### T1
- Status: todo
- Title: Summarize `.todo-scenario-4-input-a.txt` into `docs/todo-scenario-4-a.md`
- Depends on: none
- Validation: `test -f docs/todo-scenario-4-a.md`
- Blocker Type: none
- Blocker Detail: none

### T2
- Status: todo
- Title: Summarize `.todo-scenario-4-input-b.txt` into `docs/todo-scenario-4-b.md`
- Depends on: none
- Validation: `test -f docs/todo-scenario-4-b.md`
- Blocker Type: none
- Blocker Detail: none
