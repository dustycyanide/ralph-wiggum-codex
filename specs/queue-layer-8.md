# Queue Layer 8

## Goal

Verify that the durable plan stays declarative while runtime audit facts live only in run artifacts and builder JSON.

## Required Behavior

- The planner should remove any runtime-only section such as `Planner Execution State`.
- The builder should report actual context files read and skills activated in its JSON response.
- The builder should create `docs/queue-layer-8.md` with exactly:

```md
# Queue Layer 8

This file confirms runtime audit facts stayed out of the durable plan.
```
