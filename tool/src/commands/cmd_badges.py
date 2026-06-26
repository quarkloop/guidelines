"""
cmd_badges.py — `repo.py badges` subcommand.

Single responsibility: generate README badge markdown for a repository.
Produces consistent badges across all quarkloop repos.
"""

import argparse
from pathlib import Path
from typing import List


def _build_badges(repo_name: str, license_type: str, has_ci: bool = False,
                  language: str = None) -> List[str]:
    """
    Build the badge markdown lines.

    Returns a list of markdown lines (one per badge).
    """
    badges = []

    # CI badge (only if the repo has a CI workflow)
    if has_ci:
        badges.append(
            f"[![CI](https://github.com/quarkloop/{repo_name}/actions/workflows/ci.yml/badge.svg)]"
            f"(https://github.com/quarkloop/{repo_name}/actions/workflows/ci.yml)"
        )

    # License badge
    if license_type == "Apache 2.0":
        badges.append(
            "[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)"
        )
    elif license_type == "MIT":
        badges.append(
            "[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)"
        )

    # Language badge
    if language:
        lang_badges = {
            "typescript": ("TypeScript", "3178C6"),
            "go": ("Go", "00ADD8"),
            "rust": ("Rust", "CE422B"),
            "java": ("Java", "ED8B00"),
            "mixed": ("Multi", "6C757D"),
        }
        if language in lang_badges:
            label, color = lang_badges[language]
            badges.append(
                f"[![{label}](https://img.shields.io/badge/{label.replace(' ', '%20')}-{color}.svg)]"
                f"(https://go.dev/dl/)"
            )

    return badges


def _detect_license(repo: Path) -> str:
    """Detect the license type from the LICENSE file."""
    license_path = repo / "LICENSE"
    if not license_path.exists():
        return "Unknown"

    content = license_path.read_text(encoding="utf-8")
    if "Apache License" in content and "Version 2.0" in content:
        return "Apache 2.0"
    if "MIT License" in content:
        return "MIT"
    return "Unknown"


def _detect_language(repo: Path) -> str:
    """Detect the primary language from repo contents."""
    if (repo / "package.json").exists():
        return "typescript"
    if (repo / "go.mod").exists() or (repo / "go.work").exists():
        if (repo / "pom.xml").exists() or (repo / "Cargo.toml").exists():
            return "mixed"
        return "go"
    if (repo / "Cargo.toml").exists():
        return "rust"
    if (repo / "pom.xml").exists():
        return "java"
    return None


def _detect_ci(repo: Path) -> bool:
    """Check if the repo has a CI workflow."""
    ci_path = repo / ".github" / "workflows" / "ci.yml"
    return ci_path.exists()


def run(args: argparse.Namespace):
    """Execute the badges subcommand."""
    repo = Path(args.repo).resolve()

    if not repo.exists():
        print(f"Error: repository path does not exist: {repo}")
        sys.exit(2)

    # Auto-detect if not provided
    repo_name = args.repo_name or repo.name
    license_type = args.license or _detect_license(repo)
    language = args.language or _detect_language(repo)
    has_ci = args.ci if args.ci is not None else _detect_ci(repo)

    badges = _build_badges(repo_name, license_type, has_ci, language)

    if not badges:
        print("No badges to generate. Specify --license, --language, or --ci.")
        return

    print("Copy this markdown into your README.md, below the title:")
    print()
    print(" ".join(badges))
    print()
    print("Preview:")
    for badge in badges:
        print(f"  {badge}")


def add_parser(subparsers) -> None:
    """Register the badges subcommand parser."""
    parser = subparsers.add_parser(
        "badges",
        help="Generate README badge markdown",
        description=(
            "Generate consistent README badge markdown for a repository. "
            "Auto-detects license, language, and CI status from the repo "
            "contents."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Generated badges:
  - CI status (if .github/workflows/ci.yml exists)
  - License (Apache 2.0 or MIT, auto-detected from LICENSE file)
  - Language (TypeScript, Go, Rust, Java, or Multi — auto-detected)

Examples:
  python3 tool/repo.py badges --repo /path/to/repo
  python3 tool/repo.py badges --repo /path/to/repo --repo-name quark-js --license MIT --language typescript
  python3 tool/repo.py badges --repo /path/to/repo --no-ci
        """,
    )
    parser.add_argument(
        "--repo", required=True,
        help="Path to the repository",
    )
    parser.add_argument(
        "--repo-name", default=None,
        help="GitHub repo name (default: auto-detect from directory name)",
    )
    parser.add_argument(
        "--license", default=None, choices=["Apache 2.0", "MIT"],
        help="License type (default: auto-detect from LICENSE file)",
    )
    parser.add_argument(
        "--language", default=None,
        choices=["typescript", "go", "rust", "java", "mixed"],
        help="Primary language (default: auto-detect from repo contents)",
    )
    parser.add_argument(
        "--ci", action="store_true", default=None,
        help="Include CI badge (default: auto-detect from .github/workflows/ci.yml)",
    )
    parser.add_argument(
        "--no-ci", action="store_false", dest="ci",
        help="Exclude CI badge even if a CI workflow exists",
    )
    parser.set_defaults(func=run)
