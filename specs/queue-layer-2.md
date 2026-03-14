# Queue Layer 2

## Goal

Verify that the builder follows structured context-file and skill descriptors before implementation.

## Required Behavior

- The planner should identify `Q1/T1` as the active queue item.
- The builder must read `IMPLEMENTATION_PLAN.md` and `specs/queue-layer-2.md` before implementation.
- The builder should activate the required `09-implement-plan` skill before implementation.
- The builder should report actual context files read and actual skills activated in its response.
- The builder should create `docs/queue-layer-2.md` with exactly:

```md
# Queue Layer 2

This file confirms the builder respected structured context and skill descriptors.
```
