# Queue Layer 4

## Goal

Verify that queue-level shared context and shared skills are merged with item-level context.

## Required Behavior

- The planner should identify `Q1/T1` as the active queue item.
- The builder must read the queue shared spec file `specs/queue-layer-4.md` first.
- The builder must also read the item-specific code file `ralph/codex_loop.py`.
- The builder should activate the shared required skill `09-implement-plan`.
- The builder should create `docs/queue-layer-4.md` with exactly:

```md
# Queue Layer 4

This file confirms shared queue context was merged with item context.
```
