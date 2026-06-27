"""
cmd_fix.py — `repo.py fix` subcommand.

Single responsibility: automatically fix issues found by doctor that
can be safely auto-fixed. Does NOT fix issues that require human
judgment (e.g., AGENTS.md line count, README.md sections).
"""

import argparse
import shutil
import sys
from pathlib import Path
from typing import List, Tuple

from ..checks import (
    REQUIRED_FILES,
    check_required_file,
    check_editorconfig,
    check_markdownlint_config,
    check_pr_template,
    check_bug_report,
    check_feature_request,
    check_agents_guidelines_ref,
)
from ..models import CheckResult


# Files that can be auto-fixed by copying from guidelines
AUTO_FIXABLE_FILES = {
    ".editorconfig": "github/templates/editorconfig",
    ".markdownlint.json": "markdownlint/.markdownlint.json",
    ".github/ISSUE_TEMPLATE/bug_report.yml": "github/templates/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml": "github/templates/feature_request.yml",
    ".github/PULL_REQUEST_TEMPLATE.md": "github/templates/pull_request_template.md",
    ".pre-commit-config.yaml": "github/templates/pre-commit-config.yaml",
}


def _resolve_guidelines_root() -> Path:
    """Resolve the guidelines repo root from this file's location."""
    return Path(__file__).resolve().parents[3]


def _fix_missing_file(repo: Path, dest: str, source_rel: str, guidelines_root: Path) -> bool:
    """Copy a file from guidelines if it's missing or broken."""
    source = guidelines_root / source_rel
    if not source.exists():
        # Try with dot prefix for markdownlint
        source = guidelines_root / source_rel.rsplit("/", 1)[0] / f".{Path(source_rel).name}"
        if not source.exists():
            return False

    dest_path = repo / dest
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest_path)
    return True


def _fix_editorconfig(repo: Path, guidelines_root: Path) -> bool:
    """Fix .editorconfig by copying canonical version."""
    return _fix_missing_file(repo, ".editorconfig", "github/templates/editorconfig", guidelines_root)


def _fix_markdownlint(repo: Path, guidelines_root: Path) -> bool:
    """Fix .markdownlint.json by copying canonical version."""
    source = guidelines_root / "markdownlint" / ".markdownlint.json"
    if not source.exists():
        return False
    dest = repo / ".markdownlint.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return True


def _fix_pr_template(repo: Path, guidelines_root: Path) -> bool:
    """Fix PR template by copying canonical version."""
    return _fix_missing_file(repo, ".github/PULL_REQUEST_TEMPLATE.md",
                             "github/templates/pull_request_template.md", guidelines_root)


def _fix_bug_report(repo: Path, guidelines_root: Path) -> bool:
    """Fix bug report by copying canonical version."""
    return _fix_missing_file(repo, ".github/ISSUE_TEMPLATE/bug_report.yml",
                             "github/templates/bug_report.yml", guidelines_root)


def _fix_feature_request(repo: Path, guidelines_root: Path) -> bool:
    """Fix feature request by copying canonical version."""
    return _fix_missing_file(repo, ".github/ISSUE_TEMPLATE/feature_request.yml",
                             "github/templates/feature_request.yml", guidelines_root)


def _fix_pre_commit(repo: Path, guidelines_root: Path) -> bool:
    """Fix .pre-commit-config.yaml by copying canonical version."""
    return _fix_missing_file(repo, ".pre-commit-config.yaml",
                             "github/templates/pre-commit-config.yaml", guidelines_root)


def _fix_agents_guidelines_ref(repo: Path) -> bool:
    """Inject the Guidelines reference into AGENTS.md if missing."""
    agents_path = repo / "AGENTS.md"
    if not agents_path.exists():
        return False

    content = agents_path.read_text(encoding="utf-8")

    # Already has the reference
    if "quarkloop/guidelines" in content:
        return False

    # Try to inject after the Repository section
    import re
    # Find the end of the Repository section (next ## heading after ## Repository)
    pattern = r'(## Repository\n.*?)(\n## )'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        ref_line = '- **Guidelines**: [quarkloop/guidelines](https://github.com/quarkloop/guidelines)\n'
        # Insert before the next ## heading
        insertion_point = match.end() - len('\n## ')
        new_content = content[:insertion_point] + ref_line + '\n' + content[insertion_point:]
        agents_path.write_text(new_content, encoding="utf-8")
        return True

    return False


def _identify_fixes(repo: Path) -> List[Tuple[str, str]]:
    """
    Run checks and identify which issues can be auto-fixed.

    Returns a list of (check_name, fix_description) tuples.
    """
    fixable = []

    # Check each auto-fixable file
    for filepath in AUTO_FIXABLE_FILES:
        result = check_required_file(repo, filepath)
        if not result.passed:
            fixable.append((result.name, f"Copy {filepath} from guidelines"))

    # Check .editorconfig for root=true
    ec_result = check_editorconfig(repo)
    if not ec_result.passed and ec_result.message != ".editorconfig not found":
        fixable.append((ec_result.name, "Overwrite with canonical .editorconfig (has root=true)"))

    # Check PR template sections
    pr_result = check_pr_template(repo)
    if not pr_result.passed and "not found" not in pr_result.message:
        fixable.append((pr_result.name, "Overwrite with canonical PR template"))

    # Check bug report fields
    br_result = check_bug_report(repo)
    if not br_result.passed and "not found" not in br_result.message:
        fixable.append((br_result.name, "Overwrite with canonical bug report form"))

    # Check AGENTS.md guidelines ref
    ref_result = check_agents_guidelines_ref(repo)
    if not ref_result.passed:
        fixable.append((ref_result.name, "Inject Guidelines reference into AGENTS.md"))

    return fixable


def run(args: argparse.Namespace):
    """Execute the fix subcommand."""
    repo = Path(args.repo).resolve()

    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}")
        sys.exit(2)

    guidelines_root = _resolve_guidelines_root()

    # Identify what can be fixed
    fixable = _identify_fixes(repo)

    if not fixable:
        print(f"No auto-fixable issues found in {repo.name}")
        print("Run 'doctor' for a full diagnosis.")
        return

    print(f"Found {len(fixable)} auto-fixable issue(s) in {repo.name}:")
    print()
    for name, desc in fixable:
        print(f"  • {name}: {desc}")

    if args.dry_run:
        print()
        print("(dry run — no changes made)")
        return

    # Apply fixes
    print()
    print("Applying fixes...")

    fixed_count = 0

    # Fix missing files
    for filepath, source_rel in AUTO_FIXABLE_FILES.items():
        result = check_required_file(repo, filepath)
        if not result.passed:
            if _fix_missing_file(repo, filepath, source_rel, guidelines_root):
                print(f"  ✓ Fixed: {filepath} (copied from guidelines)")
                fixed_count += 1

    # Fix .editorconfig missing root=true
    ec_result = check_editorconfig(repo)
    if not ec_result.passed and ec_result.message != ".editorconfig not found":
        if _fix_editorconfig(repo, guidelines_root):
            print(f"  ✓ Fixed: .editorconfig (overwritten with canonical version)")
            fixed_count += 1

    # Fix PR template
    pr_result = check_pr_template(repo)
    if not pr_result.passed and "not found" not in pr_result.message:
        if _fix_pr_template(repo, guidelines_root):
            print(f"  ✓ Fixed: PR template (overwritten with canonical version)")
            fixed_count += 1

    # Fix bug report
    br_result = check_bug_report(repo)
    if not br_result.passed and "not found" not in br_result.message:
        if _fix_bug_report(repo, guidelines_root):
            print(f"  ✓ Fixed: bug report (overwritten with canonical form)")
            fixed_count += 1

    # Fix AGENTS.md guidelines ref
    ref_result = check_agents_guidelines_ref(repo)
    if not ref_result.passed:
        if _fix_agents_guidelines_ref(repo):
            print(f"  ✓ Fixed: AGENTS.md guidelines reference (injected)")
            fixed_count += 1

    print()
    print(f"Done: {fixed_count} issue(s) fixed.")
    print()
    print("Remaining issues (require manual fixes):")
    print("  Run 'doctor --quiet' to see what still needs attention.")


def add_parser(subparsers) -> None:
    """Register the fix subcommand parser."""
    parser = subparsers.add_parser(
        "fix",
        help="Auto-fix issues found by doctor",
        description=(
            "Automatically fix issues that can be safely auto-fixed: "
            "missing files (copy from guidelines), broken .editorconfig, "
            "outdated PR template, missing bug report fields, and missing "
            "Guidelines reference in AGENTS.md. Does NOT fix issues that "
            "require human judgment (AGENTS.md line count, README.md "
            "sections, AGENTS.md section headings)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Auto-fixable issues:
  - Missing .editorconfig, .markdownlint.json, .pre-commit-config.yaml
  - Missing issue templates (bug_report.yml, feature_request.yml)
  - Missing PR template
  - .editorconfig without root=true
  - PR template missing required sections
  - Bug report missing required fields
  - AGENTS.md missing Guidelines reference

NOT auto-fixable (requires manual work):
  - AGENTS.md line count below target
  - AGENTS.md missing required sections
  - README.md missing required sections
  - README.md over 200 lines
  - Missing AGENTS.md or README.md (run 'init' instead)
  - Missing LICENSE (run 'init' instead)
  - Missing dependabot.yml (run 'init' instead)

Examples:
  python3 tool/repo.py fix --repo /path/to/repo
  python3 tool/repo.py fix --repo /path/to/repo --dry-run
        """,
    )
    parser.add_argument(
        "--repo", required=True,
        help="Path to the repository to fix",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be fixed without making changes",
    )
    parser.set_defaults(func=run)
