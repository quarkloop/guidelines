"""
cmd_init.py — `repo.py init` subcommand.

Single responsibility: scaffold a new repository with the standard
file layout, GitHub configuration, and documentation skeletons.
"""

import argparse
from pathlib import Path
from typing import Dict

from ..archetypes import ARCHETYPES, get_archetype
from ..generator import RepoGenerator


def _build_context(args: argparse.Namespace) -> Dict[str, str]:
    """Build Jinja2 template context from CLI arguments."""
    language = args.language or "unspecified"
    license_name = "Apache 2.0"

    # Determine ecosystems for dependabot based on language and archetype
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

    # Directories for multi-dir repos
    npm_directory = "/"
    cargo_directory = "/"
    if args.type == "platform":
        npm_directory = "/web"
        cargo_directory = "/services/harness"

    return {
        "name": args.name,
        "repo_name": args.repo_name or Path(args.target).name,
        "language": language,
        "license": license_name,
        "archetype": args.type,
        "ecosystems": ecosystems,
        "ecosystem_labels": {
            "npm": "npm dependencies",
            "gomod": "Go modules",
            "maven": "Maven dependencies",
            "cargo": "Cargo (Rust) dependencies",
        },
        "ecosystem_directories": {
            "npm": npm_directory,
            "gomod": "/",
            "maven": "/",
            "cargo": cargo_directory,
        },
        # AGENTS.md placeholders
        "description": "[One-sentence statement of what this repo is and what an AI agent's job is here.]",
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


def _resolve_guidelines_root() -> Path:
    """Resolve the guidelines repo root from this file's location."""
    # This file is at guidelines/tool/src/commands/cmd_init.py
    # Guidelines root is 4 levels up
    return Path(__file__).resolve().parents[3]


def run(args: argparse.Namespace):
    """Execute the init subcommand."""
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


def add_parser(subparsers) -> None:
    """Register the init subcommand parser."""
    parser = subparsers.add_parser(
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
  python3 tool/repo.py init --type library --name "Quark Lib" --target ./quark-lib --language typescript
  python3 tool/repo.py init --type platform --name "Quark Svc" --target ./quark-svc --dry-run
        """,
    )
    parser.add_argument(
        "--type", required=True, choices=ARCHETYPES.keys(),
        help="Repository archetype",
    )
    parser.add_argument(
        "--name", required=True,
        help="Human-readable project name (e.g., 'Quark JS SDK')",
    )
    parser.add_argument(
        "--target", required=True,
        help="Target directory (will be created if it doesn't exist)",
    )
    parser.add_argument(
        "--repo-name", default=None,
        help="GitHub repo name (e.g., 'quark-js'). Defaults to --target basename.",
    )
    parser.add_argument(
        "--language", default=None,
        choices=["typescript", "go", "rust", "java", "mixed"],
        help="Primary language (affects .gitignore and dependabot config)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be created without writing files",
    )
    parser.set_defaults(func=run)
