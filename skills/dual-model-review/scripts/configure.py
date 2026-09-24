#!/usr/bin/env python3
"""Create and resolve two/three-model preferences; never invoke a model."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import re
import sys

ROLES = ("orchestrator", "second", "third")
TRANSPORTS = {"auto", "tool", "cli", "manual"}


def empty_profile():
    return {"schema_version": 1, "default_participants": 2,
            "require_distinct_providers": True, "roles": dict.fromkeys(ROLES)}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def validate_role(role, value):
    if value is None:
        return
    if not isinstance(value, dict) or set(value) != {"provider", "product", "model", "transport"}:
        raise ValueError(f"{role}: expected provider, product, model, transport")
    if not isinstance(value["provider"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", value["provider"]):
        raise ValueError(f"{role}: provider must be a canonical lowercase identifier")
    for key in ("product", "model"):
        item = value[key]
        if key == "model" and item is None:
            continue
        if not isinstance(item, str) or not item.strip() or item != item.strip():
            raise ValueError(f"{role}: {key} must be a nonempty trimmed string")
    if not isinstance(value["transport"], str) or value["transport"] not in TRANSPORTS:
        raise ValueError(f"{role}: transport must be auto, tool, cli, or manual")


def validate(profile):
    if not isinstance(profile, dict):
        raise ValueError("Expected a profile object")
    if "schema_version" in profile and (type(profile["schema_version"]) is not int
                                        or profile["schema_version"] != 1):
        raise ValueError("Unsupported schema_version; expected integer 1")
    if set(profile) != set(empty_profile()):
        raise ValueError("Expected schema_version, default_participants, require_distinct_providers, roles")
    if type(profile["default_participants"]) is not int or profile["default_participants"] not in (2, 3):
        raise ValueError("default_participants must be integer 2 or 3")
    if type(profile["require_distinct_providers"]) is not bool:
        raise ValueError("require_distinct_providers must be boolean")
    if not isinstance(profile["roles"], dict) or set(profile["roles"]) != set(ROLES):
        raise ValueError("roles must contain orchestrator, second, third (null is allowed)")
    for role, value in profile["roles"].items():
        validate_role(role, value)
    return profile


def user_path():
    return Path.home() / ".config/chust-skills/review.json"


def project_path(project):
    root = Path(project).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")
    return root / ".chust-review.json"


def select_path(explicit=None, project=None, for_write=False):
    if explicit is not None:
        return Path(explicit).expanduser().resolve(), True
    # An explicit creation destination outranks the profile selected for reading.
    if for_write and project is not None:
        return project_path(project), True
    if "CHUST_REVIEW_CONFIG" in os.environ:
        value = os.environ["CHUST_REVIEW_CONFIG"]
        if not value.strip():
            raise ValueError("CHUST_REVIEW_CONFIG is empty")
        return Path(value).expanduser().resolve(), True
    if project is not None:
        path = project_path(project)
        if path.exists():
            return path, True
    return user_path(), False


def load_profile(explicit=None, project=None):
    path, required = select_path(explicit, project)
    if not path.exists() and not required:
        return empty_profile(), None
    return validate(read_json(path)), str(path)


def plan(profile, participants=None, overrides=None, allow_same_provider=False, host=None):
    effective = copy.deepcopy(validate(profile))
    if allow_same_provider:
        effective["require_distinct_providers"] = False
    if overrides is not None:
        if not isinstance(overrides, dict) or set(overrides) - set(ROLES):
            raise ValueError("Task overrides must be an object containing only role names")
        for role, value in overrides.items():
            validate_role(role, value)
            effective["roles"][role] = copy.deepcopy(value)
    validate_role("current host", host)
    host_default_applied = (host is not None and effective["roles"]["orchestrator"] is None
                            and (overrides is None or "orchestrator" not in overrides))
    if host_default_applied:
        effective["roles"]["orchestrator"] = copy.deepcopy(host)
    count = effective["default_participants"] if participants is None else participants
    if type(count) is not int or count not in (2, 3):
        raise ValueError("participants must be integer 2 or 3")
    active = {role: effective["roles"][role] for role in ROLES[:count]}
    missing = [role for role, value in active.items() if value is None]
    selected = [(role, value) for role, value in active.items() if value is not None]
    for index, (role, value) in enumerate(selected):
        for other_role, other in selected[:index]:
            if value["provider"] != other["provider"]:
                continue
            if effective["require_distinct_providers"]:
                raise ValueError(f"{other_role} and {role} require different providers")
            if value["model"] and other["model"] and value["model"].casefold() == other["model"].casefold():
                raise ValueError(f"{other_role} and {role} select the same model")
    return {"participants": count, "roles": active,
            "host_default_applied": host_default_applied,
            "require_distinct_providers": effective["require_distinct_providers"],
            "selection_status": "NEEDS_CONFIGURATION" if missing else "READY_TO_CHECK_ACCESS",
            "missing_roles": missing, "access_status": "NOT CHECKED",
            "identity_status": "NOT CHECKED", "execution_status": "NOT RUN"}


def initialize(path, profile):
    validate(profile)
    payload = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "show", "plan"):
        command = commands.add_parser(name)
        command.add_argument("--config", help="Explicit profile path")
        command.add_argument("--project", help="Explicit project root")
        if name == "init":
            command.add_argument("--from-file", help="Import an existing preference JSON")
        elif name == "plan":
            command.add_argument("--participants", type=int, choices=(2, 3))
            command.add_argument("--roles-file", help="Temporary whole-role replacements as JSON")
            command.add_argument("--host-file", help="Known current host as one role record; fills an unspecified orchestrator")
            command.add_argument("--allow-same-provider", action="store_true",
                                 help="Task explicitly selects distinct models from one provider")
    args = parser.parse_args(argv)
    try:
        if args.action == "init":
            path, _ = select_path(args.config, args.project, for_write=True)
            profile = validate(read_json(args.from_file)) if args.from_file else empty_profile()
            initialize(path, profile)
            result = {"source": str(path), "profile": profile}
        else:
            profile, source = load_profile(args.config, args.project)
            if args.action == "show":
                result = {"source": source, "profile": profile}
            else:
                overrides = read_json(args.roles_file) if args.roles_file else None
                host = read_json(args.host_file) if args.host_file else None
                result = {"source": source, **plan(profile, args.participants, overrides,
                                                  args.allow_same_provider, host)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get("selection_status") == "NEEDS_CONFIGURATION" else 0
    except (OSError, ValueError) as exc:
        print(f"CONFIGURATION ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
