# Queue Layer 1

## Goal

Verify the first queue-aware planner/builder contract.

## Required Behavior

- The planner should identify `Q1` as the active queue.
- The planner should identify `Q1/T1` as the active queue item.
- The builder should create `docs/queue-layer-1.md` with exactly:

```md
# Queue Layer 1

This file confirms the queue baseline scenario.
```

- The next planner pass should mark the run complete.
