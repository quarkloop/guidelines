"""
checks.py — Individual validation check functions.

Single responsibility: each function performs ONE check and returns a
CheckResult. No orchestration, no state — just pure functions that
examine a repo and report a single fact.
"""

import os
from pathlib import Path
from typing import List, Optional

from .models import CheckResult


# ─── Constants ──────────────────────────────────────────────────────────

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

AGENTS_REQUIRED_SECTIONS = [
    "# Agent Guide",
    "## Repository",
    "## Quick reference",
    "## Structure",
    "## Rules",
    "## Commit conventions",
    "## Testing",
]

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

PR_REQUIRED_SECTIONS = [
    "## Description",
    "## Type of change",
    "## Checklist",
]

BUG_REPORT_REQUIRED_FIELDS = [
    "description",
    "steps",
    "expected",
    "actual",
    "version",
    "runtime-version",
    "os",
]

AGENTS_SMALL_TARGET = 200
AGENTS_LARGE_TARGET = 400
AGENTS_LARGE_THRESHOLD = 50
README_MAX_LINES = 200

SOURCE_EXTENSIONS = {".go", ".ts", ".tsx", ".rs", ".java", ".py", ".js", ".jsx"}
SKIP_DIRS = {".git", "node_modules", "target", "dist", "bin", "vendor", ".next", ".vercel", ".source"}


# ─── Utility functions ─────────────────────────────────────────────────

def _read_file(path: Path) -> Optional[str]:
    """Read a file, returning None if it doesn't exist or can't be read."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return None


def _count_lines(path: Path) -> int:
    """Count lines in a file, returning 0 if it doesn't exist."""
    content = _read_file(path)
    if content is None:
        return 0
    return len(content.splitlines())


def count_source_files(repo: Path) -> int:
    """Count source files (excluding docs, configs, node_modules, etc.)."""
    count = 0
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if Path(f).suffix in SOURCE_EXTENSIONS:
                count += 1
    return count


def is_large_repo(repo: Path) -> bool:
    """Classify a repo as large (>50 source files) or small."""
    return count_source_files(repo) > AGENTS_LARGE_THRESHOLD


# ─── File existence checks ─────────────────────────────────────────────

def check_required_file(repo: Path, filepath: str) -> CheckResult:
    """Check that a required file exists."""
    path = repo / filepath
    if path.exists():
        return CheckResult(f"Required file: {filepath}", True, f"Found: {filepath}")
    return CheckResult(f"Required file: {filepath}", False, f"Missing: {filepath}")


def check_optional_file(repo: Path, filepath: str) -> CheckResult:
    """Check if an optional file exists (passes either way, reports status)."""
    path = repo / filepath
    if path.exists():
        return CheckResult(f"Optional file: {filepath}", True, f"Found: {filepath}")
    return CheckResult(f"Optional file: {filepath}", True, f"Not present (optional): {filepath}")


# ─── AGENTS.md checks ──────────────────────────────────────────────────

def check_agents_sections(repo: Path) -> CheckResult:
    """Check AGENTS.md has all required sections."""
    content = _read_file(repo / "AGENTS.md")
    if content is None:
        return CheckResult("AGENTS.md sections", False, "AGENTS.md not found")

    missing = [s for s in AGENTS_REQUIRED_SECTIONS if s not in content]
    if missing:
        detail = "\n".join(f"  - {s}" for s in missing)
        return CheckResult(
            "AGENTS.md sections", False,
            f"Missing {len(missing)} required sections", detail,
        )
    return CheckResult(
        "AGENTS.md sections", True,
        f"All {len(AGENTS_REQUIRED_SECTIONS)} required sections present",
    )


def check_agents_guidelines_ref(repo: Path) -> CheckResult:
    """Check AGENTS.md references the guidelines repo."""
    content = _read_file(repo / "AGENTS.md")
    if content is None:
        return CheckResult("AGENTS.md guidelines ref", False, "AGENTS.md not found")

    if "quarkloop/guidelines" in content:
        return CheckResult("AGENTS.md guidelines ref", True, "References quarkloop/guidelines")
    return CheckResult("AGENTS.md guidelines ref", False, "Missing reference to quarkloop/guidelines")


def check_agents_line_count(repo: Path) -> CheckResult:
    """Check AGENTS.md line count meets the target for the repo size."""
    lines = _count_lines(repo / "AGENTS.md")
    if lines == 0:
        return CheckResult("AGENTS.md line count", False, "AGENTS.md not found or empty")

    large = is_large_repo(repo)
    target = AGENTS_LARGE_TARGET if large else AGENTS_SMALL_TARGET
    repo_type = "large" if large else "small"
    source_count = count_source_files(repo)

    if lines >= target:
        return CheckResult(
            "AGENTS.md line count", True,
            f"{lines} lines (>= {target} for {repo_type} repo)",
        )
    return CheckResult(
        "AGENTS.md line count", False,
        f"{lines} lines (< {target} target for {repo_type} repo)",
        f"Repo has {source_count} source files → classified as {repo_type} (target: {target} lines)",
    )


# ─── README.md checks ──────────────────────────────────────────────────

def check_readme_sections(repo: Path) -> CheckResult:
    """Check README.md has all required sections."""
    content = _read_file(repo / "README.md")
    if content is None:
        return CheckResult("README.md sections", False, "README.md not found")

    missing = [s for s in README_REQUIRED_SECTIONS if s not in content]
    if missing:
        detail = "\n".join(f"  - {s}" for s in missing)
        return CheckResult(
            "README.md sections", False,
            f"Missing {len(missing)} required sections", detail,
        )
    return CheckResult(
        "README.md sections", True,
        f"All {len(README_REQUIRED_SECTIONS)} required sections present",
    )


def check_readme_line_count(repo: Path) -> CheckResult:
    """Check README.md is under 200 lines."""
    lines = _count_lines(repo / "README.md")
    if lines == 0:
        return CheckResult("README.md line count", False, "README.md not found or empty")

    if lines <= README_MAX_LINES:
        return CheckResult("README.md line count", True, f"{lines} lines (<= {README_MAX_LINES})")
    return CheckResult(
        "README.md line count", False,
        f"{lines} lines (> {README_MAX_LINES} target)",
        "Move detailed content to docs/*.mdx files",
    )


# ─── GitHub config checks ──────────────────────────────────────────────

def check_editorconfig(repo: Path) -> CheckResult:
    """Check .editorconfig exists and has root=true."""
    content = _read_file(repo / ".editorconfig")
    if content is None:
        return CheckResult(".editorconfig", False, ".editorconfig not found")

    if "root = true" in content:
        return CheckResult(".editorconfig", True, "Found with root=true")
    return CheckResult(".editorconfig", False, "Missing 'root = true' directive")


def check_markdownlint_config(repo: Path) -> CheckResult:
    """Check .markdownlint.json exists."""
    path = repo / ".markdownlint.json"
    if path.exists():
        return CheckResult(".markdownlint.json", True, "Found")
    return CheckResult(".markdownlint.json", False, "Missing")


def check_dependabot(repo: Path) -> CheckResult:
    """Check .github/dependabot.yml exists."""
    path = repo / ".github" / "dependabot.yml"
    if path.exists():
        return CheckResult(".github/dependabot.yml", True, "Found")
    return CheckResult(".github/dependabot.yml", False, "Missing")


def check_pr_template(repo: Path) -> CheckResult:
    """Check PR template has all required sections."""
    content = _read_file(repo / ".github" / "PULL_REQUEST_TEMPLATE.md")
    if content is None:
        return CheckResult("PR template sections", False, "PULL_REQUEST_TEMPLATE.md not found")

    missing = [s for s in PR_REQUIRED_SECTIONS if s not in content]
    if missing:
        detail = "\n".join(f"  - {s}" for s in missing)
        return CheckResult(
            "PR template sections", False,
            f"Missing {len(missing)} required sections", detail,
        )
    return CheckResult(
        "PR template sections", True,
        f"All {len(PR_REQUIRED_SECTIONS)} required sections present",
    )


def check_bug_report(repo: Path) -> CheckResult:
    """Check bug_report.yml has required fields."""
    content = _read_file(repo / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml")
    if content is None:
        return CheckResult("Bug report template fields", False, "bug_report.yml not found")

    missing = [f for f in BUG_REPORT_REQUIRED_FIELDS if f"id: {f}" not in content]
    if missing:
        detail = "\n".join(f"  - {f}" for f in missing)
        return CheckResult(
            "Bug report template fields", False,
            f"Missing {len(missing)} required fields", detail,
        )
    return CheckResult(
        "Bug report template fields", True,
        f"All {len(BUG_REPORT_REQUIRED_FIELDS)} required fields present",
    )


def check_feature_request(repo: Path) -> CheckResult:
    """Check feature_request.yml exists."""
    path = repo / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"
    if path.exists():
        return CheckResult("Feature request template", True, "Found")
    return CheckResult("Feature request template", False, "Missing")


def check_license(repo: Path) -> CheckResult:
    """Check LICENSE file exists and contains a known license."""
    content = _read_file(repo / "LICENSE")
    if content is None:
        return CheckResult("LICENSE", False, "LICENSE not found")

    if "Apache License" in content and "Version 2.0" in content:
        return CheckResult("LICENSE", True, "Apache License 2.0")
    if "MIT License" in content:
        return CheckResult("LICENSE", True, "MIT License")
    return CheckResult("LICENSE", False, "Unknown license (expected Apache 2.0 or MIT)")


# ─── All checks registry ───────────────────────────────────────────────

def run_all_checks(repo: Path) -> List[CheckResult]:
    """
    Run every check against a repo and return all results.

    This is the only function that knows about all checks — individual
    check functions are independent and can be used in isolation.
    """
    results: List[CheckResult] = []

    # Required files
    for filepath in REQUIRED_FILES:
        results.append(check_required_file(repo, filepath))

    # Optional files
    for filepath in OPTIONAL_FILES:
        results.append(check_optional_file(repo, filepath))

    # AGENTS.md checks
    results.append(check_agents_sections(repo))
    results.append(check_agents_guidelines_ref(repo))
    results.append(check_agents_line_count(repo))

    # README.md checks
    results.append(check_readme_sections(repo))
    results.append(check_readme_line_count(repo))

    # GitHub config checks
    results.append(check_editorconfig(repo))
    results.append(check_markdownlint_config(repo))
    results.append(check_dependabot(repo))
    results.append(check_pr_template(repo))
    results.append(check_bug_report(repo))
    results.append(check_feature_request(repo))

    # License check
    results.append(check_license(repo))

    return results
