"""
cli.py — Command-line interface for quarkloop repository tooling.

Single responsibility: parse arguments and dispatch to the appropriate
subcommand (init, validate). No business logic — delegates to generator
and validator modules.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from .archetypes import ARCHETYPES, get_archetype
from .generator import RepoGenerator
from .validator import validate_repo, print_report


def _resolve_guidelines_root() -> Path:
    """Resolve the guidelines repo root from this file's location."""
    # This file is at guidelines/scripts/src/cli.py
    # Guidelines root is 3 levels up
    return Path(__file__).resolve().parents[2]


def _build_context(args: argparse.Namespace) -> Dict[str, str]:
    """Build Jinja2 template context from CLI arguments."""
    language = args.language or "unspecified"
    license_name = "Apache 2.0"

    # Determine ecosystems for dependabot based on language
    if args.type == "library":
        if language == "typescript":
            ecosystems = ["npm"]
        elif language == "go":
            ecosystems = ["gomod"]
        elif language == "rust":
            ecosystems = ["cargo"]
        elif language == "java":
            ecosystems = ["maven"]
        else:
            ecosystems = ["npm"]
    elif args.type == "platform":
        ecosystems = ["gomod", "maven"]
    elif args.type == "docs":
        ecosystems = ["npm"]
    else:
        ecosystems = []

    return {
        "name": args.name,
        "repo_name": args.repo_name or Path(args.target).name,
        "language": language,
        "license": license_name,
        "archetype": args.type,
        "ecosystems": ecosystems,
        # AGENTS.md placeholders
        "description": f"[One-sentence statement of what this repo is and what an AI agent's job is here.]",
        "build_command": f"# [build command for {language}]",
        "test_command": f"# [test command for {language}]",
        "check_command": f"# [check/lint command for {language}]",
        "e2e_command": "# [E2E test command if applicable]",
        "directories": ["src/", "docs/", "examples/"],
        "boundaries": [],
        # README.md placeholders
        "tagline": "[One-sentence tagline describing what this is]",
        "overview": "[2-3 sentences. What this is, who it's for, what problem it solves.]",
        "features": [
            {"name": "Feature 1", "description": "[description]"},
            {"name": "Feature 2", "description": "[description]"},
            {"name": "Feature 3", "description": "[description]"},
            {"name": "Feature 4", "description": "[description]"},
        ],
        "install_commands": f"# [install commands for {language}]",
        "quick_start": "# [Minimal end-to-end example]",
        "compatibility": [
            {"component": "Component", "language": language, "version": "[version]"},
        ],
        # CONTRIBUTING.md placeholders
        "prerequisites": [f"[Prerequisite 1 for {language}]", "[Prerequisite 2]"],
        "fmt_command": f"# [format command for {language}]",
        "lint_command": f"# [lint command for {language}]",
        # SECURITY.md placeholders
        "project_name": args.name,
        "in_scope_components": ["[Component 1]", "[Component 2]"],
    }


def cmd_init(args: argparse.Namespace):
    """Handle the 'init' subcommand — scaffold a new repo."""
    guidelines_root = _resolve_guidelines_root()
    target = Path(args.target).resolve()

    archetype = get_archetype(args.type)
    context = _build_context(args)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Scaffolding {args.type} repo: {args.name}")
    print(f"  Target: {target}")
    print(f"  Repo name: {context['repo_name']}")
    print(f"  Language: {context['language']}")
    print()

    # Create target directory if it doesn't exist
    if not target.exists():
        if not args.dry_run:
            target.mkdir(parents=True)
        print(f"  ✓ Created target directory: {target}")
    else:
        print(f"  • Target directory exists: {target}")

    # Generate files
    generator = RepoGenerator(guidelines_root)
    results = generator.generate(archetype, target, context, dry_run=args.dry_run)

    # Print results
    print()
    print("Directories:")
    for key, created in results.items():
        if key.startswith("dir:"):
            dir_name = key[4:]
            status = "✓ Created" if created else "• Exists"
            print(f"  {status}: {dir_name}/")

    print()
    print("Files:")
    created_count = 0
    skipped_count = 0
    for key, created in results.items():
        if key.startswith("dir:"):
            continue
        if created:
            print(f"  ✓ Created: {key}")
            created_count += 1
        else:
            print(f"  • Exists:  {key}")
            skipped_count += 1

    print()
    print(f"Done: {created_count} created, {skipped_count} skipped (already exist)")
    if args.dry_run:
        print("(dry run — no files written)")
    else:
        print()
        print("Next steps:")
        print(f"  1. cd {target}")
        print("  2. git init (if not already a git repo)")
        print("  3. Edit AGENTS.md, README.md, CONTRIBUTING.md, SECURITY.md")
        print("     Fill in the [placeholder] sections.")
        print("  4. git add -A && git commit -m 'chore: initialize repository'")
        print("  5. git remote add origin git@github.com:quarkloop/<repo>.git")
        print("  6. git push -u origin main")


def cmd_validate(args: argparse.Namespace):
    """Handle the 'validate' subcommand — check a repo against specs."""
    report = validate_repo(args.repo)

    if args.json:
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
    else:
        print(f"Validating: {report.repo_path}")
        print()
        print_report(report, quiet=args.quiet)

    sys.exit(0 if report.all_passed else 1)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="repo.py",
        description="Quarkloop repository tooling — scaffold and validate repos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ─── init subcommand ────────────────────────────────────────────
    init_parser = subparsers.add_parser(
        "init",
        help="Scaffold a new repository with required files",
        description="Scaffold a new quarkloop repository with required files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Archetypes:
  library   — single-language library (like quark-js)
  platform  — multi-language platform (like quark)
  docs      — documentation site (like docs)
  specs     — specifications repository (like guidelines)

Examples:
  python3 scripts/repo.py init --type library --name "Quark Lib" --target ./quark-lib --language typescript
  python3 scripts/repo.py init --type platform --name "Quark Svc" --target ./quark-svc --dry-run
        """,
    )
    init_parser.add_argument(
        "--type", required=True, choices=ARCHETYPES.keys(),
        help="Repository archetype",
    )
    init_parser.add_argument(
        "--name", required=True,
        help="Human-readable project name (e.g., 'Quark JS SDK')",
    )
    init_parser.add_argument(
        "--target", required=True,
        help="Target directory (will be created if it doesn't exist)",
    )
    init_parser.add_argument(
        "--repo-name", default=None,
        help="GitHub repo name (e.g., 'quark-js'). Defaults to --target basename.",
    )
    init_parser.add_argument(
        "--language", default=None,
        choices=["typescript", "go", "rust", "java", "mixed"],
        help="Primary language (affects .gitignore and dependabot config)",
    )
    init_parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be created without writing files",
    )
    init_parser.set_defaults(func=cmd_init)

    # ─── validate subcommand ────────────────────────────────────────
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a repository against quarkloop guidelines",
        description="Validate an existing repository against quarkloop guidelines.",
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
  python3 scripts/repo.py validate --repo /path/to/repo
  python3 scripts/repo.py validate --repo /path/to/repo --json
  python3 scripts/repo.py validate --repo /path/to/repo --quiet
        """,
    )
    validate_parser.add_argument(
        "--repo", required=True,
        help="Path to the repository to validate",
    )
    validate_parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON (for CI integration)",
    )
    validate_parser.add_argument(
        "--quiet", action="store_true",
        help="Only show failures (suppress passed checks)",
    )
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main():
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
