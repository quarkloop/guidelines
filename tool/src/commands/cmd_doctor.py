"""
cmd_doctor.py — `repo.py doctor` subcommand.

Single responsibility: validate a repository against quarkloop guidelines
and report results with actionable fix suggestions. Merges the old
'validate' and 'doctor' concepts into one command.
"""

import argparse
import json
import sys
from pathlib import Path

from ..checks import run_all_checks
from ..models import ValidationReport


def _validate_repo(repo_path: str) -> ValidationReport:
    """Run all checks and assemble a report."""
    repo = Path(repo_path).resolve()

    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}")
        sys.exit(2)

    if not (repo / ".git").exists():
        print(f"Warning: {repo} does not appear to be a git repository (no .git directory)")

    report = ValidationReport(repo_path=str(repo))
    report.results = run_all_checks(repo)
    return report


def _print_report(report: ValidationReport, quiet: bool = False):
    """Print the validation report in human-readable format."""
    if quiet:
        # Only print failures with suggestions
        for r in report.failed_results:
            print(f"  ✗ {r.name}: {r.message}")
            if r.detail:
                print(f"    {r.detail}")
            if r.suggestion:
                print(f"    → Fix: {r.suggestion}")
    else:
        # Print all checks
        for r in report.results:
            status = "✓" if r.passed else "✗"
            print(f"  {status} {r.name}: {r.message}")
            if r.detail:
                for line in r.detail.splitlines():
                    print(f"      {line}")
            if not r.passed and r.suggestion:
                print(f"      → Fix: {r.suggestion}")

    print()
    total = len(report.results)
    print(f"  Total: {report.passed_count}/{total} passed, {report.failed_count} failed")

    if report.all_passed:
        print("  ✓ All checks passed")
    else:
        print(f"  ✗ {report.failed_count} check(s) failed")


def _print_json_report(report: ValidationReport):
    """Print the validation report as JSON."""
    output = {
        "repo": report.repo_path,
        "passed": report.all_passed,
        "summary": {
            "total": len(report.results),
            "passed": report.passed_count,
            "failed": report.failed_count,
        },
        "checks": [
            {
                "name": r.name,
                "passed": r.passed,
                "message": r.message,
                "detail": r.detail,
                "suggestion": r.suggestion,
            }
            for r in report.results
        ],
    }
    print(json.dumps(output, indent=2))


def run(args: argparse.Namespace):
    """Execute the doctor subcommand."""
    report = _validate_repo(args.repo)

    if args.json:
        _print_json_report(report)
    else:
        print(f"Diagnosing: {report.repo_path}")
        print()
        _print_report(report, quiet=args.quiet)

    sys.exit(0 if report.all_passed else 1)


def add_parser(subparsers) -> None:
    """Register the doctor subcommand parser."""
    parser = subparsers.add_parser(
        "doctor",
        help="Validate a repository and suggest fixes",
        description=(
            "Validate an existing repository against quarkloop guidelines. "
            "Reports failures with actionable fix suggestions."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Checks:
  - Required files exist (AGENTS.md, README.md, LICENSE, etc.)
  - AGENTS.md has all required sections and the Guidelines reference
  - AGENTS.md line count meets target (>=200 small, >=400 large)
  - README.md has all required sections and is under 200 lines
  - .editorconfig exists with root=true
  - .markdownlint.json exists
  - .github/dependabot.yml exists
  - GitHub issue templates exist with required fields
  - PR template exists with required sections
  - LICENSE is Apache 2.0 or MIT

Examples:
  python3 tool/repo.py doctor --repo /path/to/repo
  python3 tool/repo.py doctor --repo /path/to/repo --json
  python3 tool/repo.py doctor --repo /path/to/repo --quiet
        """,
    )
    parser.add_argument(
        "--repo", required=True,
        help="Path to the repository to diagnose",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON (for CI integration)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Only show failures and fix suggestions",
    )
    parser.set_defaults(func=run)
