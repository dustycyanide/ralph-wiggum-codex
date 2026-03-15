# Queue Layer 7 Promotion

## Goal

Verify that the planner promotes the next queued queue once the earlier queue is done.

## Required Behavior

- `Q1` should stay completed.
- The next planner pass should promote `Q2` to active.
- The builder should execute only from `Q2`.
- The builder should create `docs/queue-layer-7.md` with exactly:

```md
# Queue Layer 7

This file confirms the planner promoted Q2 before building.
```
