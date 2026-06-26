"""
cmd_sync.py — `repo.py sync` subcommand.

Single responsibility: copy canonical template files from the guidelines
repo into an existing repo, overwriting outdated copies. Does NOT touch
files with repo-specific content (AGENTS.md, README.md, etc.).
"""

import argparse
import shutil
from pathlib import Path
from typing import Dict, List

# Files that are safe to sync (identical across all repos — no repo-specific content)
SYNCABLE_FILES: Dict[str, str] = {
    # dest path in target repo → source path in guidelines repo
    ".editorconfig": "github/templates/editorconfig",
    ".markdownlint.json": "markdownlint/.markdownlint.json",
    ".github/ISSUE_TEMPLATE/bug_report.yml": "github/templates/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml": "github/templates/feature_request.yml",
    ".github/PULL_REQUEST_TEMPLATE.md": "github/templates/pull_request_template.md",
}


def _resolve_guidelines_root() -> Path:
    """Resolve the guidelines repo root from this file's location."""
    return Path(__file__).resolve().parents[3]


def _sync_file(
    source: Path,
    dest: Path,
    dry_run: bool,
) -> str:
    """
    Copy one file from source to dest.

    Returns one of: 'updated', 'identical', 'created', 'error'
    """
    if not source.exists():
        return "error"

    if dest.exists():
        existing = dest.read_bytes()
        new = source.read_bytes()
        if existing == new:
            return "identical"

    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    return "created" if not dest.exists() or dry_run else "updated"


def run(args: argparse.Namespace):
    """Execute the sync subcommand."""
    guidelines_root = _resolve_guidelines_root()
    target = Path(args.repo).resolve()

    if not target.exists():
        print(f"Error: repository path does not exist: {target}")
        sys.exit(2)

    # Determine which files to sync
    if args.files:
        requested = [f.strip() for f in args.files.split(",")]
        files_to_sync = {
            dest: src
            for dest, src in SYNCABLE_FILES.items()
            if dest in requested or Path(dest).name in requested
        }
        if not files_to_sync:
            print(f"Error: no syncable files matched: {args.files}")
            print(f"  Available: {', '.join(SYNCABLE_FILES.keys())}")
            sys.exit(2)
    else:
        files_to_sync = SYNCABLE_FILES

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Syncing {len(files_to_sync)} files from guidelines")
    print(f"  Source: {guidelines_root}")
    print(f"  Target: {target}")
    print()

    results: Dict[str, str] = {}
    created_count = 0
    updated_count = 0
    identical_count = 0
    error_count = 0

    for dest_path, source_rel in files_to_sync.items():
        source = guidelines_root / source_rel
        dest = target / dest_path

        status = _sync_file(source, dest, args.dry_run)
        results[dest_path] = status

        if status == "created":
            print(f"  ✓ Created: {dest_path}")
            created_count += 1
        elif status == "updated":
            print(f"  ↻ Updated: {dest_path}")
            updated_count += 1
        elif status == "identical":
            print(f"  • Already current: {dest_path}")
            identical_count += 1
        else:
            print(f"  ✗ Error: {dest_path} (source not found)")
            error_count += 1

    print()
    print(f"Done: {created_count} created, {updated_count} updated, "
          f"{identical_count} already current, {error_count} errors")
    if args.dry_run:
        print("(dry run — no files written)")


def add_parser(subparsers) -> None:
    """Register the sync subcommand parser."""
    parser = subparsers.add_parser(
        "sync",
        help="Sync canonical template files from guidelines into a repo",
        description=(
            "Copy canonical template files from the guidelines repo into an "
            "existing repo, overwriting outdated copies. Only syncs files "
            "that are identical across all repos (editorconfig, markdownlint, "
            "issue templates, PR template). Does NOT touch files with "
            "repo-specific content (AGENTS.md, README.md, etc.)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Syncable files:
  .editorconfig
  .markdownlint.json
  .github/ISSUE_TEMPLATE/bug_report.yml
  .github/ISSUE_TEMPLATE/feature_request.yml
  .github/PULL_REQUEST_TEMPLATE.md

Examples:
  python3 tool/repo.py sync --repo /path/to/repo
  python3 tool/repo.py sync --repo /path/to/repo --files .editorconfig,.markdownlint.json
  python3 tool/repo.py sync --repo /path/to/repo --dry-run
        """,
    )
    parser.add_argument(
        "--repo", required=True,
        help="Path to the repository to sync into",
    )
    parser.add_argument(
        "--files", default=None,
        help="Comma-separated list of specific files to sync (default: all)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing files",
    )
    parser.set_defaults(func=run)
