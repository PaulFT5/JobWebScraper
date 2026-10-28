"""PreToolUse guard: Claude may only write inside frontend/ and tests/ plus its own tracking docs.

Backend, scraper, workflows, config, DB etc. are owned by the user and must never be
edited by Claude. Exit code 2 blocks the tool call and feeds stderr back to Claude.
"""
import json
import os
import sys
from pathlib import Path

ALLOWED_DIRS = ["frontend", "tests"]
ALLOWED_FILES = ["CLAUDE.md", "docs/ASSIST_LOG.md", "docs/BE_IMPLEMENTATION.md", "docs/MATCHING_ROADMAP.md"]


def main():
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return 0

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".").resolve()
    path = Path(target)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()

    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        # outside the project (scratchpad, memory dir, etc.) - not this guard's concern
        return 0

    if rel in ALLOWED_FILES or any(rel == d or rel.startswith(d + "/") for d in ALLOWED_DIRS):
        return 0

    print(
        f"BLOCKED by project rule: '{rel}' is not a frontend file. Claude may only modify "
        f"files under frontend/ (on request), tests/ and the tracking docs {ALLOWED_FILES}. "
        "For backend work, explain the reasoning to the user instead of editing.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
