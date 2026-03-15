# Queue Layer 5 Strict

## Goal

Verify that the planner keeps missing external input strict and blocked.

## Required Behavior

- The planner should keep the queue and active item `strict`.
- The planner should return `waiting`.
- The builder should not run.
