"""
cmd_check_commits.py — `repo.py check-commits` subcommand.

Single responsibility: validate that recent commit messages follow the
Conventional Commits format (type(scope): description).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Conventional Commit types (standard + quarkloop extensions)
VALID_TYPES = {"feat", "fix", "refactor", "docs", "test", "chore",
                "perf", "build", "ci", "style", "revert"}

# Pattern: type(scope): description  OR  type: description
# Scope is optional. Description must be non-empty.
# No trailing period on the summary line.
COMMIT_PATTERN = re.compile(
    r'^(?P<type>\w+)'
    r'(?:\((?P<scope>[\w\-/.]+)\))?'
    r':\s+'
    r'(?P<description>.+?)'
    r'\s*$'
)

# Common bad commit messages
BAD_PATTERNS = [
    (re.compile(r'^(wip|WIP|todo|TODO)\b', re.IGNORECASE), "WIP/TODO commits should be squashed before merging"),
    (re.compile(r'^fix(ed)?\s+', re.IGNORECASE), "Use 'fix:' not 'fixed ...'"),
    (re.compile(r'^update\s+', re.IGNORECASE), "Use a specific type: 'feat:', 'fix:', 'refactor:', 'docs:'"),
    (re.compile(r'^added?\s+', re.IGNORECASE), "Use 'feat:' not 'added ...'"),
    (re.compile(r'^changed?\s+', re.IGNORECASE), "Use 'refactor:' or 'feat:' not 'changed ...'"),
    (re.compile(r'^removed?\s+', re.IGNORECASE), "Use 'refactor:' or 'fix:' not 'removed ...'"),
]


def _get_commits(repo: Path, count: int = 10, rev_range: str = None) -> List[str]:
    """
    Get commit messages from git.

    Args:
        repo: Path to the git repository
        count: Number of recent commits (ignored if rev_range is given)
        rev_range: Git revision range (e.g., 'main..feature-branch')

    Returns:
        List of commit message subject lines (first line only)
    """
    if rev_range:
        cmd = ["git", "log", "--format=%s", rev_range]
    else:
        cmd = ["git", "log", f"--format=%s", f"-{count}"]

    result = subprocess.run(
        cmd,
        cwd=str(repo),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error: git log failed: {result.stderr.strip()}")
        sys.exit(2)

    return [line for line in result.stdout.strip().splitlines() if line]


def _check_commit(message: str) -> Tuple[bool, str]:
    """
    Check a single commit message.

    Returns:
        (passed, reason) — True if valid, False with explanation if not
    """
    # Check for bad patterns first
    for pattern, reason in BAD_PATTERNS:
        if pattern.match(message):
            return False, f"Bad pattern: {reason}"

    # Check Conventional Commits format
    match = COMMIT_PATTERN.match(message)
    if not match:
        return False, (
            f"Does not match 'type(scope): description' format. "
            f"Valid types: {', '.join(sorted(VALID_TYPES))}"
        )

    commit_type = match.group("type").lower()
    if commit_type not in VALID_TYPES:
        return False, (
            f"Unknown type '{commit_type}'. "
            f"Valid types: {', '.join(sorted(VALID_TYPES))}"
        )

    description = match.group("description")

    # Check description quality
    if len(description) < 10:
        return False, f"Description too short ({len(description)} chars, need >= 10)"

    if description.endswith("."):
        return False, "Description should not end with a period"

    # Check for Co-authored-by in subject (should be in body, not subject)
    if "co-authored-by" in message.lower():
        return False, "Co-authored-by belongs in the commit body, not the subject"

    return True, "OK"


def run(args: argparse.Namespace):
    """Execute the check-commits subcommand."""
    repo = Path(args.repo).resolve()

    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}")
        sys.exit(2)

    if not (repo / ".git").exists():
        print(f"Error: {repo} is not a git repository")
        sys.exit(2)

    commits = _get_commits(repo, args.count, args.range)

    if not commits:
        print("No commits to check")
        return

    print(f"Checking {len(commits)} commit(s) in {repo.name}")
    print()

    passed_count = 0
    failed_count = 0

    for commit in commits:
        # Truncate long messages for display
        display = commit[:80] + "..." if len(commit) > 80 else commit

        ok, reason = _check_commit(commit)

        if ok:
            print(f"  ✓ {display}")
            passed_count += 1
        else:
            print(f"  ✗ {display}")
            print(f"    → {reason}")
            failed_count += 1

    print()
    print(f"Total: {passed_count} passed, {failed_count} failed")

    if failed_count > 0:
        print()
        print("Valid format: type(scope): description")
        print(f"Valid types: {', '.join(sorted(VALID_TYPES))}")
        print("Examples:")
        print("  feat(core): add streaming support for batch calls")
        print("  fix(api): propagate io.ReadAll errors")
        print("  docs(readme): add installation instructions")

    sys.exit(0 if failed_count == 0 else 1)


def add_parser(subparsers) -> None:
    """Register the check-commits subcommand parser."""
    parser = subparsers.add_parser(
        "check-commits",
        help="Validate commit message format",
        description=(
            "Check recent commit messages against the Conventional Commits "
            "format (type(scope): description). Reports violations with "
            "suggestions."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Valid types: feat, fix, refactor, docs, test, chore, perf, build, ci,
style, revert

Examples:
  python3 tool/repo.py check-commits --repo /path/to/repo
  python3 tool/repo.py check-commits --repo /path/to/repo --count 20
  python3 tool/repo.py check-commits --repo /path/to/repo --range main..feature-branch
        """,
    )
    parser.add_argument(
        "--repo", required=True,
        help="Path to the git repository",
    )
    parser.add_argument(
        "--count", type=int, default=10,
        help="Number of recent commits to check (default: 10)",
    )
    parser.add_argument(
        "--range", default=None,
        help="Git revision range (e.g., 'main..feature-branch'). Overrides --count.",
    )
    parser.set_defaults(func=run)
