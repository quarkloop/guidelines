#!/usr/bin/env python3
"""
validate_repo.py — Validate a repository against quarkloop guidelines.

Checks an existing repository for compliance with the quarkloop guidelines:
- Required files exist (AGENTS.md, README.md, LICENSE, etc.)
- AGENTS.md has all 8 sections and the Guidelines reference
- README.md has all 9 sections
- AGENTS.md line count meets target (>=200 small, >=400 large)
- README.md line count is under 200
- .editorconfig exists with root=true
- .markdownlint.json exists
- .github/dependabot.yml exists
- GitHub issue templates exist with required fields
- PR template exists with 3 sections

Usage:
  python3 scripts/validate_repo.py --repo /path/to/repo
  python3 scripts/validate_repo.py --repo /path/to/repo --json
  python3 scripts/validate_repo.py --repo /path/to/repo --quiet

Exit codes:
  0 — all checks passed
  1 — one or more checks failed
  2 — invalid arguments
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─── Check result types ─────────────────────────────────────────────────

@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str = ""
    detail: str = ""


@dataclass
class ValidationReport:
    repo_path: str
    results: list = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def all_passed(self) -> bool:
        return self.failed_count == 0

    def add(self, name: str, passed: bool, message: str = "", detail: str = ""):
        self.results.append(CheckResult(name, passed, message, detail))


# ─── Required files ─────────────────────────────────────────────────────

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "LICENSE",
    ".editorconfig",
    ".markdownlint.json",
    ".github/dependabot.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
]

OPTIONAL_FILES = [
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".markdownlintignore",
]

# ─── AGENTS.md section requirements ─────────────────────────────────────

AGENTS_REQUIRED_SECTIONS = [
    "# Agent Guide",
    "## Repository",
    "## Quick reference",
    "## Structure",
    "## Rules",
    "## Commit conventions",
    "## Testing",
]

AGENTS_OPTIONAL_SECTIONS = [
    "## Boundaries",
    "## When you're stuck",
]

AGENTS_SMALL_TARGET = 200  # lines
AGENTS_LARGE_TARGET = 400  # lines
AGENTS_LARGE_THRESHOLD = 50  # if repo has >50 source files, it's "large"


# ─── README.md section requirements ─────────────────────────────────────

README_REQUIRED_SECTIONS = [
    "## Overview",
    "## Features",
    "## Installation",
    "## Quick start",
    "## Documentation",
    "## Compatibility",
    "## Contributing",
    "## License",
]

README_MAX_LINES = 200


# ─── PR template section requirements ───────────────────────────────────

PR_REQUIRED_SECTIONS = [
    "## Description",
    "## Type of change",
    "## Checklist",
]


# ─── Bug report required fields ─────────────────────────────────────────

BUG_REPORT_REQUIRED_FIELDS = [
    "description",
    "steps",
    "expected",
    "actual",
    "version",
    "runtime-version",
    "os",
]


# ─── Helper functions ───────────────────────────────────────────────────

def count_source_files(repo: Path) -> int:
    """Count source files (excluding docs, configs, node_modules, etc.)."""
    source_extensions = {".go", ".ts", ".tsx", ".rs", ".java", ".py", ".js", ".jsx"}
    skip_dirs = {".git", "node_modules", "target", "dist", "bin", "vendor", ".next", ".vercel", ".source"}

    count = 0
    for root, dirs, files in os.walk(repo):
        # Skip excluded directories in-place
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if Path(f).suffix in source_extensions:
                count += 1
    return count


def read_file(path: Path) -> Optional[str]:
    """Read a file, returning None if it doesn't exist or can't be read."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None


def count_lines(path: Path) -> int:
    """Count lines in a file, returning 0 if it doesn't exist."""
    content = read_file(path)
    if content is None:
        return 0
    return len(content.splitlines())


# ─── Check functions ────────────────────────────────────────────────────

def check_file_exists(report: ValidationReport, repo: Path, filepath: str, required: bool = True):
    """Check if a file exists."""
    path = repo / filepath
    exists = path.exists()
    label = "Required" if required else "Optional"
    if exists:
        report.add(
            f"{label} file: {filepath}",
            True,
            f"Found: {filepath}",
        )
    else:
        report.add(
            f"{label} file: {filepath}",
            not required,  # optional files pass even if missing
            f"Missing: {filepath}" if required else f"Not present (optional): {filepath}",
        )


def check_agents_sections(report: ValidationReport, repo: Path):
    """Check AGENTS.md has all required sections."""
    content = read_file(repo / "AGENTS.md")
    if content is None:
        report.add("AGENTS.md sections", False, "AGENTS.md not found")
        return

    missing = []
    for section in AGENTS_REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)

    if missing:
        report.add(
            "AGENTS.md sections",
            False,
            f"Missing {len(missing)} required sections",
            "\n".join(f"  - {s}" for s in missing),
        )
    else:
        report.add(
            "AGENTS.md sections",
            True,
            f"All {len(AGENTS_REQUIRED_SECTIONS)} required sections present",
        )


def check_agents_guidelines_ref(report: ValidationReport, repo: Path):
    """Check AGENTS.md references the guidelines repo."""
    content = read_file(repo / "AGENTS.md")
    if content is None:
        report.add("AGENTS.md guidelines ref", False, "AGENTS.md not found")
        return

    if "quarkloop/guidelines" in content:
        report.add("AGENTS.md guidelines ref", True, "References quarkloop/guidelines")
    else:
        report.add("AGENTS.md guidelines ref", False, "Missing reference to quarkloop/guidelines")


def check_agents_line_count(report: ValidationReport, repo: Path, source_file_count: int):
    """Check AGENTS.md line count meets target."""
    lines = count_lines(repo / "AGENTS.md")
    if lines == 0:
        report.add("AGENTS.md line count", False, "AGENTS.md not found or empty")
        return

    is_large = source_file_count > AGENTS_LARGE_THRESHOLD
    target = AGENTS_LARGE_TARGET if is_large else AGENTS_SMALL_TARGET
    repo_type = "large" if is_large else "small"

    if lines >= target:
        report.add(
            "AGENTS.md line count",
            True,
            f"{lines} lines (>= {target} for {repo_type} repo)",
        )
    else:
        report.add(
            "AGENTS.md line count",
            False,
            f"{lines} lines (< {target} target for {repo_type} repo)",
            f"Repo has {source_file_count} source files → classified as {repo_type} (target: {target} lines)",
        )


def check_readme_sections(report: ValidationReport, repo: Path):
    """Check README.md has all required sections."""
    content = read_file(repo / "README.md")
    if content is None:
        report.add("README.md sections", False, "README.md not found")
        return

    missing = []
    for section in README_REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)

    if missing:
        report.add(
            "README.md sections",
            False,
            f"Missing {len(missing)} required sections",
            "\n".join(f"  - {s}" for s in missing),
        )
    else:
        report.add(
            "README.md sections",
            True,
            f"All {len(README_REQUIRED_SECTIONS)} required sections present",
        )


def check_readme_line_count(report: ValidationReport, repo: Path):
    """Check README.md is under 200 lines."""
    lines = count_lines(repo / "README.md")
    if lines == 0:
        report.add("README.md line count", False, "README.md not found or empty")
        return

    if lines <= README_MAX_LINES:
        report.add(
            "README.md line count",
            True,
            f"{lines} lines (<= {README_MAX_LINES})",
        )
    else:
        report.add(
            "README.md line count",
            False,
            f"{lines} lines (> {README_MAX_LINES} target)",
            "Move detailed content to docs/*.mdx files",
        )


def check_editorconfig(report: ValidationReport, repo: Path):
    """Check .editorconfig exists and has root=true."""
    content = read_file(repo / ".editorconfig")
    if content is None:
        report.add(".editorconfig", False, ".editorconfig not found")
        return

    if "root = true" in content:
        report.add(".editorconfig", True, "Found with root=true")
    else:
        report.add(".editorconfig", False, "Missing 'root = true' directive")


def check_markdownlint(report: ValidationReport, repo: Path):
    """Check .markdownlint.json exists."""
    path = repo / ".markdownlint.json"
    if path.exists():
        report.add(".markdownlint.json", True, "Found")
    else:
        report.add(".markdownlint.json", False, "Missing")


def check_dependabot(report: ValidationReport, repo: Path):
    """Check .github/dependabot.yml exists."""
    path = repo / ".github" / "dependabot.yml"
    if path.exists():
        report.add(".github/dependabot.yml", True, "Found")
    else:
        report.add(".github/dependabot.yml", False, "Missing")


def check_pr_template(report: ValidationReport, repo: Path):
    """Check PR template has all required sections."""
    content = read_file(repo / ".github" / "PULL_REQUEST_TEMPLATE.md")
    if content is None:
        report.add("PR template sections", False, "PULL_REQUEST_TEMPLATE.md not found")
        return

    missing = []
    for section in PR_REQUIRED_SECTIONS:
        if section not in content:
            missing.append(section)

    if missing:
        report.add(
            "PR template sections",
            False,
            f"Missing {len(missing)} required sections",
            "\n".join(f"  - {s}" for s in missing),
        )
    else:
        report.add(
            "PR template sections",
            True,
            f"All {len(PR_REQUIRED_SECTIONS)} required sections present",
        )


def check_bug_report(report: ValidationReport, repo: Path):
    """Check bug_report.yml has required fields."""
    content = read_file(repo / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml")
    if content is None:
        report.add("Bug report template", False, "bug_report.yml not found")
        return

    missing = []
    for field_id in BUG_REPORT_REQUIRED_FIELDS:
        # Look for `id: <field_id>` in the YAML
        if f"id: {field_id}" not in content:
            missing.append(field_id)

    if missing:
        report.add(
            "Bug report template fields",
            False,
            f"Missing {len(missing)} required fields",
            "\n".join(f"  - {field_id}" for field_id in missing),
        )
    else:
        report.add(
            "Bug report template fields",
            True,
            f"All {len(BUG_REPORT_REQUIRED_FIELDS)} required fields present",
        )


def check_feature_request(report: ValidationReport, repo: Path):
    """Check feature_request.yml exists."""
    path = repo / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"
    if path.exists():
        report.add("Feature request template", True, "Found")
    else:
        report.add("Feature request template", False, "Missing")


def check_license(report: ValidationReport, repo: Path):
    """Check LICENSE file exists and contains a known license."""
    content = read_file(repo / "LICENSE")
    if content is None:
        report.add("LICENSE", False, "LICENSE not found")
        return

    # Check for known license identifiers
    if "Apache License" in content and "Version 2.0" in content:
        report.add("LICENSE", True, "Apache License 2.0")
    elif "MIT License" in content:
        report.add("LICENSE", True, "MIT License")
    else:
        report.add("LICENSE", False, "Unknown license (expected Apache 2.0 or MIT)")


# ─── Main validation ────────────────────────────────────────────────────

def validate_repo(repo_path: str) -> ValidationReport:
    """Run all validation checks on a repository."""
    repo = Path(repo_path).resolve()

    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}")
        sys.exit(2)

    if not (repo / ".git").exists():
        print(f"Warning: {repo} does not appear to be a git repository (no .git directory)")

    report = ValidationReport(repo_path=str(repo))

    # Count source files for size classification
    source_count = count_source_files(repo)

    # ─── Required files ─────────────────────────────────────────────
    for filepath in REQUIRED_FILES:
        check_file_exists(report, repo, filepath, required=True)

    for filepath in OPTIONAL_FILES:
        check_file_exists(report, repo, filepath, required=False)

    # ─── AGENTS.md checks ───────────────────────────────────────────
    check_agents_sections(report, repo)
    check_agents_guidelines_ref(report, repo)
    check_agents_line_count(report, repo, source_count)

    # ─── README.md checks ───────────────────────────────────────────
    check_readme_sections(report, repo)
    check_readme_line_count(report, repo)

    # ─── GitHub config checks ───────────────────────────────────────
    check_editorconfig(report, repo)
    check_markdownlint(report, repo)
    check_dependabot(report, repo)
    check_pr_template(report, repo)
    check_bug_report(report, repo)
    check_feature_request(report, repo)

    # ─── License check ──────────────────────────────────────────────
    check_license(report, repo)

    return report


def print_report(report: ValidationReport, quiet: bool = False):
    """Print the validation report in human-readable format."""
    if quiet:
        # Only print failures
        for r in report.results:
            if not r.passed:
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


def print_json_report(report: ValidationReport):
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
            }
            for r in report.results
        ],
    }
    print(json.dumps(output, indent=2))


# ─── CLI ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate a repository against quarkloop guidelines.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Checks:
  - Required files exist (AGENTS.md, README.md, LICENSE, etc.)
  - AGENTS.md has all 8 sections and the Guidelines reference
  - AGENTS.md line count meets target (>=200 small, >=400 large)
  - README.md has all 9 sections and is under 200 lines
  - .editorconfig exists with root=true
  - .markdownlint.json exists
  - .github/dependabot.yml exists
  - GitHub issue templates exist with required fields
  - PR template exists with 3 sections
  - LICENSE is Apache 2.0 or MIT

Examples:
  python3 scripts/validate_repo.py --repo /path/to/repo
  python3 scripts/validate_repo.py --repo /path/to/repo --json
  python3 scripts/validate_repo.py --repo /path/to/repo --quiet
        """,
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the repository to validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show failures (suppress passed checks)",
    )

    args = parser.parse_args()

    report = validate_repo(args.repo)

    if args.json:
        print_json_report(report)
    else:
        print(f"Validating: {report.repo_path}")
        print()
        print_report(report, quiet=args.quiet)

    sys.exit(0 if report.all_passed else 1)


if __name__ == "__main__":
    main()
