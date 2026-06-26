"""
cmd_list.py — `repo.py list` subcommand.

Single responsibility: discover all quarkloop repos in a workspace
directory, run doctor on each, and print a summary table.
"""

import argparse
from pathlib import Path
from typing import List, Tuple

from ..checks import run_all_checks, count_source_files, _count_lines
from ..models import ValidationReport


# Repos to skip (not quarkloop product repos)
SKIP_DIRS = {".git", "node_modules", "target", "dist", "bin", "vendor",
             ".next", ".vercel", ".source", "__pycache__", "upload",
             "download", "tool-results", "skills"}


def _discover_repos(workspace: Path) -> List[Path]:
    """Find all git repos in a workspace directory."""
    repos = []
    for child in sorted(workspace.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith(".") or child.name in SKIP_DIRS:
            continue
        if (child / ".git").exists():
            repos.append(child)
    return repos


def _quick_validate(repo: Path) -> Tuple[int, int, int, int, bool]:
    """
    Run checks and return summary stats.

    Returns: (total_checks, passed, failed, agents_lines, readme_lines, all_passed)
    """
    results = run_all_checks(repo)
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    agents_lines = _count_lines(repo / "AGENTS.md")
    readme_lines = _count_lines(repo / "README.md")
    all_passed = failed == 0
    return len(results), passed, failed, agents_lines, readme_lines, all_passed


def run(args: argparse.Namespace):
    """Execute the list subcommand."""
    workspace = Path(args.workspace).resolve()

    if not workspace.exists():
        print(f"Error: workspace path does not exist: {workspace}")
        sys.exit(2)

    repos = _discover_repos(workspace)

    if not repos:
        print(f"No git repositories found in {workspace}")
        return

    print(f"Found {len(repos)} repositories in {workspace}")
    print()

    # Table header
    print(f"{'Repo':<20} {'Checks':<10} {'AGENTS':<10} {'README':<10} {'Status'}")
    print(f"{'─' * 20} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10}")

    all_pass = True
    for repo in repos:
        total, passed, failed, agents, readme, ok = _quick_validate(repo)

        checks_str = f"{passed}/{total}"
        agents_str = str(agents) if agents > 0 else "—"
        readme_str = str(readme) if readme > 0 else "—"
        status = "✓ PASS" if ok else "✗ FAIL"

        if not ok:
            all_pass = False

        print(f"{repo.name:<20} {checks_str:<10} {agents_str:<10} {readme_str:<10} {status}")

    print()
    if all_pass:
        print("  ✓ All repositories pass")
    else:
        failing = sum(1 for repo in repos
                      if not _quick_validate(repo)[5])
        print(f"  ✗ {failing} repository(ies) have failures")
        print(f"  Run: python3 tool/repo.py doctor --repo <path>  for details")


def add_parser(subparsers) -> None:
    """Register the list subcommand parser."""
    parser = subparsers.add_parser(
        "list",
        help="List all repos and their validation status",
        description=(
            "Discover all git repositories in a workspace directory, run "
            "guideline checks on each, and print a summary table."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example output:
  Repo                Checks     AGENTS     README     Status
  ─────────────────── ────────── ────────── ────────── ──────────
  quark-js            26/26      201        99         ✓ PASS
  agent               26/26      403        89         ✓ PASS
  quark               25/26      400        81         ✗ FAIL

Examples:
  python3 tool/repo.py list --workspace /home/z/my-project
  python3 tool/repo.py list --workspace .
        """,
    )
    parser.add_argument(
        "--workspace", required=True,
        help="Path to the workspace directory containing repos",
    )
    parser.set_defaults(func=run)
