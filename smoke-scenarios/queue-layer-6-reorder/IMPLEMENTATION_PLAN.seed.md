# Implementation Plan

## Goal

Run queue layer 6 reorder smoke scenario and confirm dependency metadata can reorder queue items durably.

## Queue List

### Q1
- Status: active
- Title: Dependency-aware queue reordering
- Execution Mode: strict
- Planner Decision: strict
- Planner Decision Reason: Reorder first, then execute only the first runnable item.
- Depends On Queues: none
- Completion Rule: all_todos_done
- Risk Level: low
- Side Effect Level: low
- Reversibility: easy

#### T1
- Status: todo
- Title: Create `docs/queue-layer-6-b.md`
- Execution Mode: strict
- Planner Decision: strict
- Planner Decision Reason: Blocked on prerequisite.
- Depends On Todos: T2
- Depends On Queues: none
- Unlocks: none
- Validation: `diff -u docs/queue-layer-6-b.md <(printf '# Queue Layer 6 B\n\nThis file should not be created in the first pass.\n')`
- Context Files:
  - Path: `specs/queue-layer-6-reorder.md`
  - Mode: read_in_full
  - Requirement: required
  - Trigger: always
  - Reason: reorder contract
- Required Skills:
  - Name: `09-implement-plan`
  - Mode: required
  - Trigger: always
  - Reason: implementation workflow
- Blocker Type: sequencing
- Blocker Detail: Waits on the later prerequisite item.
- Side Effect Level: low
- Reversibility: easy

#### T2
- Status: todo
- Title: Create `docs/queue-layer-6-a.md`
- Execution Mode: strict
- Planner Decision: strict
- Planner Decision Reason: Unlocks the dependent item.
- Depends On Todos: none
- Depends On Queues: none
- Unlocks: T1
- Validation: `diff -u docs/queue-layer-6-a.md <(printf '# Queue Layer 6 A\n\nThis file confirms unlock metadata reordered the queue.\n')`
- Context Files:
  - Path: `specs/queue-layer-6-reorder.md`
  - Mode: read_in_full
  - Requirement: required
  - Trigger: always
  - Reason: exact output contract
- Required Skills:
  - Name: `09-implement-plan`
  - Mode: required
  - Trigger: always
  - Reason: implementation workflow
- Blocker Type: none
- Blocker Detail: none
- Side Effect Level: low
- Reversibility: easy
