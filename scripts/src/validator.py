"""
validator.py — Orchestrates checks and produces validation reports.

Single responsibility: run all checks against a repo and assemble a
ValidationReport. Does NOT contain check logic itself — delegates to
checks.py.
"""

import sys
from pathlib import Path

from .checks import run_all_checks
from .models import ValidationReport


def validate_repo(repo_path: str) -> ValidationReport:
    """
    Run all validation checks on a repository.

    Args:
        repo_path: Path to the repository to validate

    Returns:
        ValidationReport with all check results
    """
    repo = Path(repo_path).resolve()

    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}")
        sys.exit(2)

    if not (repo / ".git").exists():
        print(f"Warning: {repo} does not appear to be a git repository (no .git directory)")

    report = ValidationReport(repo_path=str(repo))
    report.results = run_all_checks(repo)

    return report


def print_report(report: ValidationReport, quiet: bool = False):
    """Print the validation report in human-readable format."""
    if quiet:
        for r in report.failed_results:
            print(f"  ✗ {r.name}: {r.message}")
            if r.detail:
                print(f"    {r.detail}")
    else:
        for r in report.results:
            status = "✓" if r.passed else "✗"
            print(f"  {status} {r.name}: {r.message}")
            if r.detail:
                for line in r.detail.splitlines():
                    print(f"      {line}")

    print()
    total = len(report.results)
    print(f"  Total: {report.passed_count}/{total} passed, {report.failed_count} failed")

    if report.all_passed:
        print("  ✓ All checks passed")
    else:
        print(f"  ✗ {report.failed_count} check(s) failed")
