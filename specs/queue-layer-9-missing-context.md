# Queue Layer 9 Missing Context

## Goal

Verify that the builder blocks when a previously-available required context file disappears and the planner converts that contract issue into durable blocker state.

## Required Behavior

- The builder must block because a required context file is missing.
- The builder must not create `docs/queue-layer-9.md`.
- The next planner pass should keep the issue in durable blocker metadata.
