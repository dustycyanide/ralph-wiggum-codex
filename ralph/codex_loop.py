#!/usr/bin/env python3
"""Ralph-style planner/builder loop powered by codex exec."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any


EXIT_SUCCESS = 0
EXIT_INCOMPLETE = 2
EXIT_FAILED = 3


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def config_override(value: str) -> str:
    if "=" not in value:
        raise argparse.ArgumentTypeError("must be in KEY=VALUE form")
    key, _, raw = value.partition("=")
    if not key.strip():
        raise argparse.ArgumentTypeError("override key cannot be empty")
    if not raw.strip():
        raise argparse.ArgumentTypeError("override value cannot be empty")
    return value


def non_negative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ralph-style Codex loop: planner (5.3 high) + builder (5.2 high)."
    )
    parser.add_argument("task_parts", nargs="*", help="Task text (optional positional form).")
    parser.add_argument("--task", help="Task text (preferred explicit form).")
    parser.add_argument("--task-file", help="Path to a file containing task text.")

    parser.add_argument("--loops", type=positive_int, default=5, help="Max planner loops.")
    parser.add_argument(
        "--iterations",
        type=positive_int,
        default=4,
        help="Max builder iterations per planner loop.",
    )

    parser.add_argument("--plan-model", default="gpt-5.3-codex", help="Planner model.")
    parser.add_argument("--build-model", default="gpt-5.2-codex", help="Builder model.")
    parser.add_argument(
        "--plan-reasoning",
        default="high",
        help='Planner reasoning effort override (used as -c model_reasoning_effort="...").',
    )
    parser.add_argument(
        "--build-reasoning",
        default="high",
        help='Builder reasoning effort override (used as -c model_reasoning_effort="...").',
    )

    parser.add_argument(
        "--sandbox",
        choices=["read-only", "workspace-write", "danger-full-access"],
        default="workspace-write",
        help="Codex sandbox mode.",
    )
    parser.add_argument(
        "--blocked-policy",
        choices=["stop", "next-loop", "continue"],
        default="stop",
        help="Behavior when builder reports blocked status.",
    )
    parser.add_argument(
        "--plan-config",
        action="append",
        default=[],
        type=config_override,
        metavar="KEY=VALUE",
        help="Extra planner -c config override (repeatable).",
    )
    parser.add_argument(
        "--build-config",
        action="append",
        default=[],
        type=config_override,
        metavar="KEY=VALUE",
        help="Extra builder -c config override (repeatable).",
    )

    parser.add_argument("--run-dir", help="Explicit run output directory.")
    parser.add_argument(
        "--background",
        action="store_true",
        help="Run the loop in background and return PID + log path.",
    )
    parser.add_argument(
        "--pause-before-builder-seconds",
        type=non_negative_float,
        default=0.0,
        help="Optional debug pause between planner and builder steps.",
    )

    parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        dest="skip_git_repo_check",
        default=True,
        help="Pass --skip-git-repo-check to codex exec (default: enabled).",
    )
    parser.add_argument(
        "--no-skip-git-repo-check",
        action="store_false",
        dest="skip_git_repo_check",
        help="Do not pass --skip-git-repo-check to codex exec.",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="Enable live web search during codex exec steps.",
    )

    return parser


def resolve_task(args: argparse.Namespace) -> str:
    if args.task:
        task = args.task.strip()
        if task:
            return task

    if args.task_file:
        path = Path(args.task_file)
        if not path.exists():
            raise SystemExit(f"Task file not found: {path}")
        content = path.read_text(encoding="utf-8").strip()
        if content:
            return content

    positional = " ".join(args.task_parts).strip()
    if positional:
        return positional

    raise SystemExit("No task supplied. Use --task, --task-file, or positional task text.")


def resolve_run_dir(args: argparse.Namespace) -> Path:
    if args.run_dir:
        run_dir = Path(args.run_dir)
    else:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = Path(".ralph-runs") / f"run-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir.resolve()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(data) + "\n")


def safe_rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path.resolve())


def format_history(events: list[dict[str, Any]], limit: int = 10) -> str:
    if not events:
        return "(no previous loop events)"

    rendered: list[str] = []
    for event in events[-limit:]:
        kind = event.get("type", "unknown")
        if kind == "planner":
            response = event.get("response", {})
            rendered.append(
                f"- planner loop {event.get('loop')}: done={response.get('done')} | "
                f"summary={response.get('summary', '')}"
            )
            continue
        if kind == "builder":
            response = event.get("response", {})
            issue_type = response.get("issue_type") or ""
            issue_detail = response.get("issue_detail") or ""
            issue_suffix = ""
            if issue_type or issue_detail:
                issue_suffix = f" | issue={issue_type or '(unspecified)'}: {issue_detail}"
            rendered.append(
                f"- builder loop {event.get('loop')} iter {event.get('iteration')}: "
                f"status={response.get('status')} done={response.get('done')} | "
                f"summary={response.get('summary', '')}{issue_suffix}"
            )
            continue
        if kind == "error":
            rendered.append(f"- error: {event.get('message', '')}")
            continue
        rendered.append(f"- {kind}: {json.dumps(event, ensure_ascii=True)}")

    return "\n".join(rendered)


def planner_prompt(
    *,
    goal: str,
    loop_index: int,
    total_loops: int,
    max_iterations: int,
    events: list[dict[str, Any]],
) -> str:
    return textwrap.dedent(
        f"""
        You are the planning phase in a Ralph-style autonomous coding loop.

        Goal:
        {goal}

        Loop context:
        - Outer loop: {loop_index}/{total_loops}
        - Build iterations available in this loop: {max_iterations}

        Recent event history:
        {format_history(events)}

        Instructions:
        0) Ignore unrelated workflow skills or ticketing routines; focus only on this goal.
        1) Use IMPLEMENTATION_PLAN.md as the durable source of truth for the feature list, queue list,
           and queue items.
        2) Maintain an ordered feature list with ids (F1, F2, ...), an ordered queue list with ids
           (Q1, Q2, ...), and ordered todo ids within each queue (T1, T2, ...).
        3) Each feature should have at least: status, title, depends on features, completion rule,
           and the queues it owns.
        4) Each queue should have at least: status, title, execution mode (strict | optimistic |
           planner_decides), planner decision (strict | optimistic), planner decision reason, dependencies,
           completion rule, risk level, side effect level (low | medium | high), reversibility
           (easy | moderate | hard), promotion mode (strict_sequence | planner_decides), promotion reason,
           shared context file descriptors, and shared skill descriptors.
        5) Each queue item should have at least: status, title, execution mode (strict | optimistic |
           planner_decides), planner decision (strict | optimistic), planner decision reason, dependencies,
           unlocks, validation, blocker type, blocker detail, side effect level (low | medium | high),
           reversibility (easy | moderate | hard), structured context file descriptors, and structured
           skill descriptors.
        6) Context file descriptors must use this shape: path, mode (read_in_full | skim | inspect_if_needed),
           requirement (required | optional | conditional), trigger, and reason. Skill descriptors must use
           this shape: name, mode (required | optional | conditional), trigger, and reason.
           If a field is absent, preserve the existing intent and use none/empty rather than inventing new
           required context or skills. Only add required descriptors when the plan, spec, or recent contract
           issues explicitly justify them.
        7) Under strict queue order, only the first unfinished queue may be active. Do not start later queues
           while an earlier queue is unfinished unless the plan explicitly records a different planner decision.
           When an earlier queue is complete and the next queue is queued, promote that next queue to active
           if its promotion mode allows it, and record the promotion reason durably in the plan.
           Promotion must not pre-mark the promoted queue or its todos as completed/done before the builder runs.
        8) Reorder queue items inside the active queue so the first unfinished runnable item is first.
           If you reorder items, renumber todo ids to match the new order so execution decisions are stored
           durably in the plan itself.
           Use Depends On Todos, Depends On Queues, and Unlocks to make the ordering explainable.
        9) If a queue or item uses execution mode planner_decides, you may mark it optimistic only when the
           remaining blocker is sequencing-only and the work has side effect level low and reversibility easy.
           Missing external input, missing required context, or medium/high side effects must remain strict
           and blocked.
           Record the final planner decision and reason durably in IMPLEMENTATION_PLAN.md.
        10) Keep IMPLEMENTATION_PLAN.md declarative and durable. Do not create or preserve runtime audit
           sections such as "Planner Execution State", "Actual Context Files Read", "Actual Skills Activated",
           or "Builder Contract Issues". Use recent event history and run artifacts for runtime facts instead.
           If a recent builder event reports a contract issue that is still relevant, consume it into durable
           blocker metadata on the affected queue/item instead of leaving it only as runtime history.
        11) Do not implement product work yourself. You may inspect files, run checks, and edit only
           IMPLEMENTATION_PLAN.md while planning. Do not create or modify implementation artifacts.
        12) Mark a feature completed only when all queues it owns are completed. Builder execution must still
           operate only at queue/item granularity, never at feature granularity.
        13) If all features, queues, and queue items are done, set status="completed" and done=true.
        14) If the active queue has at least one runnable item now, set status="ready", done=false, and
            provide active_queue_id, active_queue_title, active_todo_id, active_todo_title, and build_objective.
        15) If unfinished work remains but the active queue has no runnable item, set status="waiting" and
            done=false.
        16) completion_criteria should be a concrete checklist to evaluate global completion.
        17) plan_updates should summarize any feature/queue/item reordering or plan-file changes you made.
        18) Use confidence between 0 and 1.

        Return JSON only, matching the provided schema.
        """
    ).strip()


def builder_prompt(
    *,
    goal: str,
    objective: str,
    active_queue_id: str,
    active_queue_title: str,
    active_todo_id: str,
    active_todo_title: str,
    completion_criteria: list[str],
    loop_index: int,
    loop_total: int,
    iteration_index: int,
    iteration_total: int,
    events: list[dict[str, Any]],
) -> str:
    criteria_lines = "\n".join(f"- {line}" for line in completion_criteria) or "- (not provided)"
    return textwrap.dedent(
        f"""
        You are the implementation phase in a Ralph-style autonomous coding loop.

        Global goal:
        {goal}

        Objective for this implementation step:
        {objective}

        Active queue selected by planner:
        - id: {active_queue_id or "(none provided)"}
        - title: {active_queue_title or "(none provided)"}

        Active todo selected by planner:
        - id: {active_todo_id or "(none provided)"}
        - title: {active_todo_title or "(none provided)"}

        Completion criteria from planner:
        {criteria_lines}

        Loop context:
        - Outer loop: {loop_index}/{loop_total}
        - Builder iteration: {iteration_index}/{iteration_total}

        Recent event history:
        {format_history(events)}

        Instructions:
        0) Ignore unrelated workflow skills or ticketing routines; focus only on this goal.
        1) Execute only the planner-selected queue item in the planner-selected active queue.
           Do not choose a different queue or item yourself.
        2) Before doing work, inspect IMPLEMENTATION_PLAN.md and verify the selected queue is still active
           and the selected todo is still the first runnable unfinished item in that queue.
        3) Read queue-level shared context file descriptors first, then read item-level context file
           descriptors. A context descriptor has: path, mode, requirement, trigger, and reason. For
           descriptors marked read_in_full or required, you must read the file before implementation.
           For optional or conditional descriptors, read them only if their trigger condition actually
           applies. If the trigger is absent, do not read or report that file. Item-level context may extend
           shared context, but it must not silently remove a required shared descriptor.
        4) Activate or follow queue-level shared skill descriptors first, then item-level skill descriptors.
           A skill descriptor has: name, mode, trigger, and reason. For skills marked required, activate
           them before implementation. For optional or conditional skills, activate them only if their trigger
           condition actually applies. Item-level skills may extend shared skills, but they must not silently
           remove a required shared skill.
        5) Report only the declared shared/item context descriptor paths you actually read in
           context_files_read, in the order read. Do not include skill files or unrelated exploration there.
           Report only skill names actually activated in skills_activated.
        6) If a required context file or required skill cannot be satisfied, treat that as a contract issue.
        7) If there is no runnable todo, no todos exist, all todos are already done, or the planner/builder
           contract is invalid, do not implement anything. Set issue_type and issue_detail, set status="blocked",
           and return. Do not add runtime audit or contract sections to IMPLEMENTATION_PLAN.md.
        8) Keep IMPLEMENTATION_PLAN.md limited to durable queue/item metadata, blockers, ordering, and
           progress. Put runtime facts only in the builder response and run artifacts.
        9) Do not create a missing prerequisite unless the active todo explicitly says to create it, or the
           missing prerequisite already exists as another todo in IMPLEMENTATION_PLAN.md.
        10) Run relevant checks/tests for the files you touched.
        11) Keep IMPLEMENTATION_PLAN.md up to date with progress on the active todo.
        12) If the active todo is complete, set status="completed" and todo_status="done".
        13) If the active todo is blocked by a real dependency or missing required input, set status="blocked"
           and todo_status="blocked".
        14) Otherwise set status="in_progress" and provide a clear next_objective for the same active todo.
        15) Keep stop_reason concise and explicit.

        Return JSON only, matching the provided schema.
        """
    ).strip()


def append_event(state: dict[str, Any], state_file: Path, event: dict[str, Any]) -> None:
    state.setdefault("events", []).append(event)
    write_json(state_file, state)


def write_step_log(
    *,
    path: Path,
    command: list[str],
    prompt: str,
    stdout: str,
    stderr: str,
    return_code: int,
) -> None:
    lines = [
        f"$ {shlex.join(command)}",
        "",
        "[prompt]",
        prompt,
        "",
        "[stdout]",
        stdout.rstrip(),
        "",
        "[stderr]",
        stderr.rstrip(),
        "",
        f"[return_code] {return_code}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run_codex_step(
    *,
    model: str,
    reasoning: str,
    sandbox: str,
    schema_path: Path,
    output_file: Path,
    log_file: Path,
    prompt: str,
    skip_git_repo_check: bool,
    search: bool,
    config_overrides: list[str],
) -> dict[str, Any]:
    command = ["codex", "exec"]
    if skip_git_repo_check:
        command.append("--skip-git-repo-check")

    command.extend(
        [
            "--model",
            model,
            "--sandbox",
            sandbox,
            "--output-schema",
            str(schema_path.resolve()),
            "--output-last-message",
            str(output_file.resolve()),
            "--color",
            "never",
            "--ephemeral",
            "-c",
            f'model_reasoning_effort="{reasoning}"',
        ]
    )

    if search:
        command.append("--search")

    for item in config_overrides:
        command.extend(["-c", item])

    command.append("-")

    proc = subprocess.run(
        command,
        input=prompt,
        text=True,
        capture_output=True,
        check=False,
    )

    write_step_log(
        path=log_file,
        command=command,
        prompt=prompt,
        stdout=proc.stdout,
        stderr=proc.stderr,
        return_code=proc.returncode,
    )

    if proc.returncode != 0:
        raise RuntimeError(f"codex exec failed (exit {proc.returncode}); see {safe_rel(log_file)}")

    if not output_file.exists():
        raise RuntimeError(f"Missing expected output file: {safe_rel(output_file)}")

    raw = output_file.read_text(encoding="utf-8").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Could not parse JSON output from {safe_rel(output_file)}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"Output JSON must be an object in {safe_rel(output_file)}")

    return data


def background_spawn(run_dir: Path) -> int:
    child_args = [arg for arg in sys.argv[1:] if arg != "--background"]
    if "--run-dir" not in child_args:
        child_args.extend(["--run-dir", str(run_dir)])

    command = [sys.executable, str(Path(__file__).resolve()), *child_args]
    log_file = run_dir / "background.log"
    with log_file.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(  # noqa: S603
            command,
            cwd=str(Path.cwd()),
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    pid_file = run_dir / "pid.txt"
    pid_file.write_text(f"{process.pid}\n", encoding="utf-8")

    print(f"Background run started.")
    print(f"Run directory: {safe_rel(run_dir)}")
    print(f"Log file: {safe_rel(log_file)}")
    print(f"PID: {process.pid}")
    print(f"Stop with: kill {process.pid}")
    return EXIT_SUCCESS


def build_initial_state(task: str, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "started_at": utc_now_iso(),
        "task": task,
        "config": {
            "loops": args.loops,
            "iterations": args.iterations,
            "plan_model": args.plan_model,
            "build_model": args.build_model,
            "plan_reasoning": args.plan_reasoning,
            "build_reasoning": args.build_reasoning,
            "sandbox": args.sandbox,
            "blocked_policy": args.blocked_policy,
            "skip_git_repo_check": args.skip_git_repo_check,
            "search": args.search,
            "pause_before_builder_seconds": args.pause_before_builder_seconds,
        },
        "events": [],
        "status": "running",
    }


def finalize(
    *,
    state: dict[str, Any],
    state_file: Path,
    run_dir: Path,
    status: str,
    reason: str,
) -> int:
    state["status"] = status
    state["finished_at"] = utc_now_iso()
    state["final_reason"] = reason
    write_json(state_file, state)

    result = {
        "status": status,
        "reason": reason,
        "run_dir": safe_rel(run_dir),
        "state_file": safe_rel(state_file),
        "finished_at": state["finished_at"],
    }
    result_file = run_dir / "result.json"
    write_json(result_file, result)

    print(json.dumps(result, indent=2))
    if status == "completed":
        return EXIT_SUCCESS
    if status in {"incomplete", "blocked", "waiting"}:
        return EXIT_INCOMPLETE
    return EXIT_FAILED


def run_loop(args: argparse.Namespace, task: str, run_dir: Path) -> int:
    schema_dir = Path(__file__).resolve().parent / "schemas"
    planner_schema = schema_dir / "plan.schema.json"
    builder_schema = schema_dir / "build.schema.json"

    if not planner_schema.exists() or not builder_schema.exists():
        missing = [path for path in [planner_schema, builder_schema] if not path.exists()]
        raise SystemExit(f"Missing schema file(s): {', '.join(safe_rel(path) for path in missing)}")

    state_file = run_dir / "state.json"
    task_file = run_dir / "task.txt"
    builder_issues_file = run_dir / "builder-issues.jsonl"
    task_file.write_text(task + "\n", encoding="utf-8")

    state = build_initial_state(task, args)
    write_json(state_file, state)

    for loop_idx in range(1, args.loops + 1):
        planner_output = run_dir / f"loop-{loop_idx:02d}-planner.json"
        planner_log = run_dir / f"loop-{loop_idx:02d}-planner.log"

        plan_prompt = planner_prompt(
            goal=task,
            loop_index=loop_idx,
            total_loops=args.loops,
            max_iterations=args.iterations,
            events=state["events"],
        )

        try:
            plan_response = run_codex_step(
                model=args.plan_model,
                reasoning=args.plan_reasoning,
                sandbox=args.sandbox,
                schema_path=planner_schema,
                output_file=planner_output,
                log_file=planner_log,
                prompt=plan_prompt,
                skip_git_repo_check=args.skip_git_repo_check,
                search=args.search,
                config_overrides=args.plan_config,
            )
        except Exception as exc:  # noqa: BLE001
            append_event(
                state,
                state_file,
                {
                    "type": "error",
                    "timestamp": utc_now_iso(),
                    "phase": "planner",
                    "loop": loop_idx,
                    "message": str(exc),
                },
            )
            return finalize(
                state=state,
                state_file=state_file,
                run_dir=run_dir,
                status="failed",
                reason=f"Planner execution failed in loop {loop_idx}: {exc}",
            )

        append_event(
            state,
            state_file,
            {
                "type": "planner",
                "timestamp": utc_now_iso(),
                "loop": loop_idx,
                "response": plan_response,
                "output_file": safe_rel(planner_output),
                "log_file": safe_rel(planner_log),
            },
        )

        if bool(plan_response.get("done")):
            reason = str(plan_response.get("stop_reason") or "Planner marked task complete.")
            return finalize(
                state=state,
                state_file=state_file,
                run_dir=run_dir,
                status="completed",
                reason=reason,
            )

        planner_status = str(plan_response.get("status") or "")
        if planner_status == "waiting":
            reason = str(plan_response.get("stop_reason") or "Planner marked remaining work as waiting.")
            return finalize(
                state=state,
                state_file=state_file,
                run_dir=run_dir,
                status="waiting",
                reason=reason,
            )

        current_objective = str(plan_response.get("build_objective") or "").strip()
        if not current_objective:
            current_objective = "Make measurable progress toward the global goal."

        active_queue_id = str(plan_response.get("active_queue_id") or "").strip()
        active_queue_title = str(plan_response.get("active_queue_title") or "").strip()
        active_todo_id = str(plan_response.get("active_todo_id") or "").strip()
        active_todo_title = str(plan_response.get("active_todo_title") or "").strip()

        criteria_raw = plan_response.get("completion_criteria")
        if isinstance(criteria_raw, list):
            criteria = [str(item) for item in criteria_raw if str(item).strip()]
        else:
            criteria = []

        for iter_idx in range(1, args.iterations + 1):
            builder_output = run_dir / f"loop-{loop_idx:02d}-iter-{iter_idx:02d}-builder.json"
            builder_log = run_dir / f"loop-{loop_idx:02d}-iter-{iter_idx:02d}-builder.log"

            if args.pause_before_builder_seconds > 0:
                time.sleep(args.pause_before_builder_seconds)

            step_prompt = builder_prompt(
                goal=task,
                objective=current_objective,
                active_queue_id=active_queue_id,
                active_queue_title=active_queue_title,
                active_todo_id=active_todo_id,
                active_todo_title=active_todo_title,
                completion_criteria=criteria,
                loop_index=loop_idx,
                loop_total=args.loops,
                iteration_index=iter_idx,
                iteration_total=args.iterations,
                events=state["events"],
            )

            try:
                build_response = run_codex_step(
                    model=args.build_model,
                    reasoning=args.build_reasoning,
                    sandbox=args.sandbox,
                    schema_path=builder_schema,
                    output_file=builder_output,
                    log_file=builder_log,
                    prompt=step_prompt,
                    skip_git_repo_check=args.skip_git_repo_check,
                    search=args.search,
                    config_overrides=args.build_config,
                )
            except Exception as exc:  # noqa: BLE001
                append_event(
                    state,
                    state_file,
                    {
                        "type": "error",
                        "timestamp": utc_now_iso(),
                        "phase": "builder",
                        "loop": loop_idx,
                        "iteration": iter_idx,
                        "message": str(exc),
                    },
                )
                return finalize(
                    state=state,
                    state_file=state_file,
                    run_dir=run_dir,
                    status="failed",
                    reason=f"Builder execution failed in loop {loop_idx}, iteration {iter_idx}: {exc}",
                )

            append_event(
                state,
                state_file,
                {
                    "type": "builder",
                    "timestamp": utc_now_iso(),
                    "loop": loop_idx,
                    "iteration": iter_idx,
                    "response": build_response,
                    "output_file": safe_rel(builder_output),
                    "log_file": safe_rel(builder_log),
                },
            )

            status = str(build_response.get("status", "in_progress"))
            stop_reason = str(build_response.get("stop_reason") or "No stop reason provided.")
            issue_type = str(build_response.get("issue_type") or "").strip()
            issue_detail = str(build_response.get("issue_detail") or "").strip()

            if issue_type or issue_detail:
                append_jsonl(
                    builder_issues_file,
                    {
                        "timestamp": utc_now_iso(),
                        "loop": loop_idx,
                        "iteration": iter_idx,
                        "active_queue_id": active_queue_id,
                        "active_todo_id": str(build_response.get("active_todo_id") or active_todo_id),
                        "status": status,
                        "todo_status": str(build_response.get("todo_status") or ""),
                        "issue_type": issue_type,
                        "issue_detail": issue_detail,
                        "stop_reason": stop_reason,
                    },
                )

            if status == "blocked":
                break

            if status == "completed":
                break

            next_objective = str(build_response.get("next_objective") or "").strip()
            if next_objective:
                current_objective = next_objective

    return finalize(
        state=state,
        state_file=state_file,
        run_dir=run_dir,
        status="incomplete",
        reason=(
            f"Hit loop/iteration cap without completion (loops={args.loops}, "
            f"iterations={args.iterations})."
        ),
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    task = resolve_task(args)
    run_dir = resolve_run_dir(args)

    if args.background:
        return background_spawn(run_dir)

    try:
        return run_loop(args, task, run_dir)
    except KeyboardInterrupt:
        print("Interrupted by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
