#!/usr/bin/env python3
"""Jump to the next agent needing attention.

Ranks agents from `herdr agent list` by a configurable status priority
and focuses the top one. If the currently focused agent is itself in the
ranked list, jumps to the one after it, so repeated presses cycle through
every agent needing attention.
"""

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

DEFAULT_CONFIG = """\
# Agent statuses that count as "needs attention", highest priority first.
# Statuses not listed are never jumped to.
# Known statuses: blocked, done, working, idle, unknown
priority = ["blocked", "done", "idle"]

# "all" = consider agents in every workspace; "workspace" = active workspace only
scope = "all"
"""

DEFAULTS = {
    "priority": ["blocked", "done", "idle"],
    "scope": "all",
}


def herdr_bin():
    # HERDR_BIN_PATH may carry a " (deleted)" suffix after an in-place update.
    bin_path = os.environ.get("HERDR_BIN_PATH", "").removesuffix(" (deleted)")
    if bin_path and Path(bin_path).is_file():
        return bin_path
    return shutil.which("herdr") or str(Path.home() / ".local/bin/herdr")


def load_config():
    config_dir = os.environ.get("HERDR_PLUGIN_CONFIG_DIR")
    if not config_dir:
        return dict(DEFAULTS)
    path = Path(config_dir) / "config.toml"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(DEFAULT_CONFIG)
    try:
        raw = tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError) as e:
        print(f"next-agent: ignoring invalid {path}: {e}", file=sys.stderr)
        raw = {}
    config = dict(DEFAULTS)
    if isinstance(raw.get("priority"), list):
        config["priority"] = [s for s in raw["priority"] if isinstance(s, str)]
    if raw.get("scope") in ("all", "workspace"):
        config["scope"] = raw["scope"]
    return config


def run_herdr(*args):
    result = subprocess.run(
        [herdr_bin(), *args], capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        print(f"next-agent: herdr {' '.join(args)} failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def main():
    config = load_config()
    priority = config["priority"]

    agents = json.loads(run_herdr("agent", "list"))["result"]["agents"]

    if config["scope"] == "workspace":
        workspace = os.environ.get("HERDR_ACTIVE_WORKSPACE_ID") or os.environ.get("HERDR_WORKSPACE_ID")
        if workspace:
            agents = [a for a in agents if a.get("workspace_id") == workspace]

    ranked = sorted(
        (a for a in agents if a.get("agent_status") in priority),
        key=lambda a: (priority.index(a["agent_status"]), a.get("terminal_id", "")),
    )
    if not ranked:
        return

    target = ranked[0]
    for i, a in enumerate(ranked):
        if a.get("focused"):
            target = ranked[(i + 1) % len(ranked)]
            break

    run_herdr("agent", "focus", target["terminal_id"])


if __name__ == "__main__":
    main()
