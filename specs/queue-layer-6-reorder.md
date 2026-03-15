# Queue Layer 6 Reorder

## Goal

Verify that dependency and unlock metadata let the planner reorder queue items durably.

## Required Behavior

- The planner should reorder the queue so the unlocker task comes first.
- The builder should only execute the newly-first item.
- The builder should create `docs/queue-layer-6-a.md` with exactly:

```md
# Queue Layer 6 A

This file confirms unlock metadata reordered the queue.
```
