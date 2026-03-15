# Queue Layer 5 Optimistic

## Goal

Verify that the planner can durably mark low-risk sequencing-only work as optimistic and proceed.

## Required Behavior

- The planner should mark the queue and active item `optimistic`.
- The builder should proceed with `Q1/T1`.
- The builder should create `docs/queue-layer-5-optimistic.md` with exactly:

```md
# Queue Layer 5 Optimistic

This file confirms the planner proceeded optimistically on sequencing-only work.
```
