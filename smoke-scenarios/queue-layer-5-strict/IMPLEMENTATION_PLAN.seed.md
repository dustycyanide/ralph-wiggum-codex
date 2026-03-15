# Implementation Plan

## Goal

Run queue layer 5 strict smoke scenario and confirm missing external input remains strict and blocked.

## Queue List

### Q1
- Status: active
- Title: Planner-owned strict external-input decision
- Execution Mode: planner_decides
- Planner Decision: strict
- Planner Decision Reason: Pending planner review.
- Depends On Queues: none
- Completion Rule: all_todos_done
- Risk Level: low
- Side Effect Level: low
- Reversibility: easy

#### T1
- Status: blocked
- Title: Wait for external input before creating `docs/queue-layer-5-strict.md`
- Execution Mode: planner_decides
- Planner Decision: strict
- Planner Decision Reason: Pending planner review.
- Depends On Todos: none
- Depends On Queues: none
- Validation: not_applicable_until_external_input_arrives
- Context Files:
  - Path: `specs/queue-layer-5-strict.md`
  - Mode: read_in_full
  - Requirement: required
  - Trigger: always
  - Reason: blocking contract
- Required Skills:
  - Name: `09-implement-plan`
  - Mode: required
  - Trigger: only_if_external_input_arrives
  - Reason: implementation workflow
- Blocker Type: external_input
- Blocker Detail: A required external input has not arrived and must not be invented.
- Risk Level: low
- Side Effect Level: low
- Reversibility: easy
