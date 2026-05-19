"""
CLI for the InParallel compliance checker.

Run from the repo root:

    python -m compliance_checker.main
    python -m compliance_checker.main --workspace "Marketing"
    python -m compliance_checker.main --include-transcripts
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Allow running both as ``python -m compliance_checker.main`` and as
# ``python compliance_checker/main.py`` from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from client import InParallelClient  # noqa: E402

from compliance_checker.checker import ComplianceChecker  # noqa: E402
from compliance_checker.report import format_report  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="InParallel compliance checker")
    parser.add_argument(
        "--workspace",
        help="Workspace name to match (case-insensitive). Defaults to the first workspace.",
    )
    parser.add_argument(
        "--include-transcripts",
        action="store_true",
        help="Also scan meeting transcripts for sensitive data (opt-in, README §12.2).",
    )
    return parser.parse_args()


async def _resolve_workspace(
    client: InParallelClient, name: str | None
) -> tuple[str, str]:
    raw = await client.list_workspaces()
    workspaces = json.loads(raw) if isinstance(raw, str) else raw or []
    if not workspaces:
        raise SystemExit("No workspaces accessible with the current API key.")

    if not name:
        ws = workspaces[0]
        return ws["id"], ws.get("name", ws["id"])

    needle = name.lower()
    matches = [w for w in workspaces if needle in (w.get("name", "")).lower()]
    if not matches:
        names = ", ".join(w.get("name", "?") for w in workspaces)
        raise SystemExit(f"No workspace matches '{name}'. Available: {names}")
    if len(matches) > 1:
        names = ", ".join(w.get("name", "?") for w in matches)
        raise SystemExit(f"Workspace '{name}' is ambiguous. Matches: {names}")
    ws = matches[0]
    return ws["id"], ws.get("name", ws["id"])


async def _run(args: argparse.Namespace) -> None:
    async with InParallelClient() as ip:
        workspace_id, workspace_name = await _resolve_workspace(ip, args.workspace)
        checker = ComplianceChecker(
            ip,
            workspace_id,
            workspace_name=workspace_name,
            include_transcripts=args.include_transcripts,
        )
        report = await checker.run()
        print(format_report(report))


def main() -> None:
    asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    main()
