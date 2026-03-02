# Ralph + Codex research notes

## Source playbook reviewed

- Main guide used: `https://github.com/ghuntley/how-to-ralph-wiggum`
- Key file set from that repo (`files/`):
  - `loop.sh`
  - `PROMPT_plan.md`
  - `PROMPT_build.md`
  - `AGENTS.md`
  - `IMPLEMENTATION_PLAN.md`

The core pattern is a dumb outer loop with persistent on-disk state (`IMPLEMENTATION_PLAN.md`) and fresh model context each iteration.

## Codex CLI findings

- Correct background-safe non-interactive command is `codex exec`.
- There is no `codex exec-c` command.
- `-c` means config override. Example:

  ```bash
  -c 'model_reasoning_effort="high"'
  ```

- `codex exec` supports:
  - `--output-schema`
  - `--output-last-message`
  - `--sandbox`
  - `--skip-git-repo-check`

These are enough to build deterministic planner/builder loop orchestration.

References:

- `codex exec --help` (local CLI, v0.104.0)
- `https://developers.openai.com/codex/noninteractive`
- `https://developers.openai.com/codex/cli/reference`

## Model routing findings

- Codex model docs list both `gpt-5.3-codex` and `gpt-5.2-codex` for CLI usage.
- The docs position 5.3 as most capable and 5.2 as previous generation.

Reference:

- `https://developers.openai.com/codex/models`

## Decisions applied in this repository

- Planner defaults to `gpt-5.3-codex` + high reasoning.
- Builder defaults to `gpt-5.2-codex` + high reasoning.
- Execution uses `codex exec` with JSON schema outputs for reliable machine control.
- Loop can stop itself when planner or builder reports completion.
- Blocked behavior is configurable (`stop`, `next-loop`, `continue`).
