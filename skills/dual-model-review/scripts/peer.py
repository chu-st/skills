#!/usr/bin/env python3
"""Deliver a supplied-corpus brief to a real peer. Standard library only."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def native_executable(value):
    resolved = shutil.which(value) or (str(Path(value).resolve()) if Path(value).is_file() else None)
    if not resolved:
        raise ValueError(f"Executable not found: {value}. Set --executable or CHUST_<PROVIDER>_BIN.")
    resolved = str(Path(resolved).resolve())
    if os.name == "nt" and Path(resolved).suffix.lower() in {".bat", ".cmd"}:
        raise ValueError("Use a native executable, not a Windows .cmd/.bat shell wrapper. "
                         "Locate the provider's .exe with Get-Command <provider> -All or its "
                         "official installation guide, then pass --executable <absolute-path>.")
    return resolved


def command_for(args, output):
    if args.provider == "command":
        if not args.command_file:
            raise ValueError("--command-file is required for the command adapter")
        parts = json.loads(Path(args.command_file).read_text(encoding="utf-8-sig"))
        if not isinstance(parts, list) or not parts or not all(isinstance(x, str) for x in parts):
            raise ValueError("Command file must be a nonempty JSON array of strings")
        if not any("{model}" in x for x in parts[1:]):
            raise ValueError("Command adapter must pass {model} explicitly")
        return [native_executable(parts[0])] + [x.replace("{model}", args.model) for x in parts[1:]]
    executable = native_executable(args.executable or os.environ.get(
        f"CHUST_{args.provider.upper()}_BIN", args.provider))
    if args.provider == "claude":
        return [executable, "-p", "--model", args.model, "--safe-mode", "--tools", "",
                "--strict-mcp-config", "--no-session-persistence", "--output-format", "json"]
    return [executable, "exec", "--skip-git-repo-check", "--ephemeral", "--ignore-user-config",
            "--sandbox", "read-only", "--color", "never", "--model", args.model,
            "--json", "--output-last-message", str(output / "provider-response.md"), "-"]


def stop_process(proc):
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        proc.wait(timeout=5)


def extract_response(provider, output):
    raw = (output / "stdout.log").read_text(encoding="utf-8-sig", errors="replace")
    reported = None
    if provider == "claude":
        payload = json.loads(raw)
        # Claude may return a full message array in some print configurations.
        if isinstance(payload, list):
            results = [x for x in payload if isinstance(x, dict) and x.get("type") == "result"]
            payload = results[-1] if results else {}
        if not isinstance(payload, dict) or payload.get("is_error") or payload.get("subtype") != "success":
            raise ValueError("Claude did not return a successful result envelope")
        response = payload.get("result", "")
        reported = payload.get("model")
        if not reported:
            usage = payload.get("modelUsage", {})
            if isinstance(usage, dict):
                # Token volume does not identify the author when several models ran.
                candidates = [k for k, v in usage.items() if isinstance(v, dict)
                              and isinstance(v.get("outputTokens"), (int, float))
                              and not isinstance(v.get("outputTokens"), bool)
                              and v["outputTokens"] > 0]
                if len(candidates) == 1:
                    reported = candidates[0]
    elif provider == "codex":
        final_path = output / "provider-response.md"
        if not final_path.is_file():
            raise ValueError("Codex did not create its last-message artifact")
        response = final_path.read_text(encoding="utf-8-sig")
        events = [json.loads(line) for line in raw.splitlines() if line.strip()]
        if not all(isinstance(x, dict) for x in events):
            raise ValueError("Codex returned an invalid event envelope")
        if not any(x.get("type") == "turn.completed" for x in events):
            raise ValueError("Codex response has no completed turn")
        if any(x.get("type") == "turn.failed" for x in events):
            raise ValueError("Codex reported a failed turn")
        # Codex JSON events do not consistently expose the resolved model identity.
        models = {x["model"] for x in events if isinstance(x.get("model"), str) and x["model"].strip()}
        reported = next(iter(models)) if len(models) == 1 else None
    else:
        response = raw
    if not isinstance(response, str) or not response.strip():
        raise ValueError("Peer returned an empty answer")
    return response.strip() + "\n", reported if isinstance(reported, str) and reported.strip() else None


def model_identity(provider, requested, reported):
    """Compare reported identity conservatively; an alias is not a resolved ID."""
    if not reported:
        return {"status": "UNVERIFIED", "basis": "No unambiguous model identity was reported"}
    family_aliases = {"opus", "sonnet", "haiku"}
    if provider == "claude" and requested in family_aliases:
        family = re.match(r"^claude-(?:[0-9]+(?:-[0-9]+)*-)?(opus|sonnet|haiku)(?:-|$)", reported)
        if family:
            matches = family.group(1) == requested
            return {"status": "FAMILY_MATCH" if matches else "MISMATCH",
                    "basis": "Reported Claude family matches; the alias's exact version is not verified"
                    if matches else "Reported Claude family differs from the requested family"}
        return {"status": "UNVERIFIED", "basis": "The Claude alias was not resolved to a recognizable model ID"}
    known_id = r"^(?:claude-(?:[0-9]+(?:-[0-9]+)*-)?(?:opus|sonnet|haiku)-[0-9]|gpt-[0-9]|o[0-9](?:-|$))"
    if not re.match(known_id, requested) or not re.match(known_id, reported):
        return {"status": "UNVERIFIED", "basis": "Unknown alias or model ID; compare with the provider's diagnostics"}
    if requested == reported:
        return {"status": "MATCH", "basis": "Requested and reported identifiers match exactly"}
    date_suffix = r"-(?:[0-9]{8}|[0-9]{4}-[0-9]{2}-[0-9]{2})$"
    requested_base = re.sub(date_suffix, "", requested)
    reported_base = re.sub(date_suffix, "", reported)
    if requested_base == reported_base and ((requested_base == requested) != (reported_base == reported)):
        return {"status": "UNVERIFIED", "basis": "A dated model ID and an unresolved alias cannot be confirmed equal"}
    return {"status": "MISMATCH", "basis": "Reported model differs from the requested model ID"}


def extract_usage(provider, output):
    """Preserve provider counters; do not invent comparable totals or bills."""
    try:
        raw = (output / "stdout.log").read_text(encoding="utf-8-sig")
        if provider == "claude":
            payload = json.loads(raw)
            if isinstance(payload, list):
                payload = next((x for x in reversed(payload) if isinstance(x, dict)
                                and x.get("type") == "result"), {})
            source = "claude.result"
            keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
            counters, cost = payload.get("usage", {}), payload.get("total_cost_usd")
        elif provider == "codex":
            events = [json.loads(line) for line in raw.splitlines() if line.strip()]
            payload = next((x for x in reversed(events) if isinstance(x, dict)
                            and x.get("type") in {"turn.completed", "turn.failed"}), {})
            source = "codex." + payload.get("type", "unknown")
            keys = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                    "output_tokens", "reasoning_output_tokens")
            counters, cost = payload.get("usage", {}), None
        else:
            return None
        def number(value):
            return (isinstance(value, (int, float)) and not isinstance(value, bool)
                    and math.isfinite(value) and value >= 0)
        values = {key: counters[key] for key in keys if number(counters.get(key))}
        result = {"source": source, "tokens": values}
        status = payload.get("subtype") if provider == "claude" else payload.get("type")
        if isinstance(status, str):
            result["result_status"] = status
        if number(cost):
            result["reported_cost_usd"] = cost
        return result if values or "reported_cost_usd" in result else None
    except (OSError, ValueError, TypeError, AttributeError):
        return None


def run(args):
    brief = sys.stdin.read() if args.prompt == "-" else Path(args.prompt).read_text(encoding="utf-8-sig")
    if not brief.strip():
        raise ValueError("Empty brief; no model was called")
    if args.timeout <= 0:
        raise ValueError("Timeout must be positive")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    input_bytes = brief.encode("utf-8")
    (output / "input.md").write_bytes(input_bytes)
    receipt = {"schema": "chust-peer/v1", "execution_status": "NOT RUN", "quality_verdict": "NOT ASSESSED",
               "provider": args.provider, "requested_model": args.model, "reported_model": None,
               "model_identity": model_identity(args.provider, args.model, None),
               "started_at": timestamp(), "input_sha256": digest(input_bytes),
               "exit_code": None, "response_sha256": None}
    write_json(output / "receipt.json", receipt)
    start = time.monotonic()
    proc = None
    try:
        command = command_for(args, output)
        receipt["argv"] = command
        write_json(output / "receipt.json", receipt)
        print(f"Calling {args.provider} / {args.model}; logs: {output}", flush=True)
        flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                    cwd=output, shell=False, creationflags=flags,
                                    start_new_session=os.name != "nt")
            receipt["pid"] = proc.pid
            write_json(output / "receipt.json", receipt)
            try:
                proc.communicate(brief.encode("utf-8"), timeout=args.timeout)
            except subprocess.TimeoutExpired:
                stop_process(proc)
                raise ValueError(f"Peer timed out after {args.timeout}s; partial logs preserved")
        receipt["exit_code"] = proc.returncode
        if proc.returncode != 0:
            raise ValueError(f"Peer exited {proc.returncode}; see stderr.log and stdout.log")
        response, reported = extract_response(args.provider, output)
        response_bytes = response.encode("utf-8")
        (output / "response.md").write_bytes(response_bytes)
        identity = model_identity(args.provider, args.model, reported)
        receipt.update(reported_model=reported, model_identity=identity,
                       response_sha256=digest(response_bytes))
        if identity["status"] == "MISMATCH":
            raise ValueError(f"Requested {args.model}, but the provider reported {reported}; "
                             "the answer is preserved, but the requested model review is NOT RUN")
        receipt["execution_status"] = "PASS"
        return_code = 0
    except (OSError, ValueError, subprocess.SubprocessError, KeyboardInterrupt) as exc:
        if proc:
            stop_process(proc)
            receipt["exit_code"] = proc.returncode
        receipt["error"] = str(exc) or "Interrupted"
        return_code = 2
    finally:
        receipt.update(finished_at=timestamp(), elapsed_seconds=round(time.monotonic() - start, 3))
        receipt["usage"] = extract_usage(args.provider, output)
        write_json(output / "receipt.json", receipt)
    print(json.dumps({"execution_status": receipt["execution_status"],
                      "requested_model": receipt["requested_model"], "reported_model": receipt["reported_model"],
                      "model_identity": receipt["model_identity"], "receipt": str(output / "receipt.json"),
                      "error": receipt.get("error")}, ensure_ascii=False), flush=True)
    return return_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["claude", "codex", "command"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", required=True, help="UTF-8 brief path, or - for stdin")
    parser.add_argument("--output", required=True, help="New result directory; never overwritten")
    parser.add_argument("--executable")
    parser.add_argument("--command-file")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    try:
        return run(args)
    except (OSError, ValueError) as exc:
        print(f"NOT RUN: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
