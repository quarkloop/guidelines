"""
cmd_setup.py — `repo.py setup` subcommand.

Single responsibility: clone quarkloop repos and install pre-commit hooks
in a single repo or all repos in a workspace.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

# The main quarkloop product repos
PRODUCT_REPOS = {
    "quark": "git@github.com:quarkloop/quark.git",
    "agent": "git@github.com:quarkloop/agent.git",
    "quark-js": "git@github.com:quarkloop/quark-js.git",
    "docs": "git@github.com:quarkloop/docs.git",
    "guidelines": "git@github.com:quarkloop/guidelines.git",
}


def _check_pre_commit() -> bool:
    """Check if pre-commit is installed."""
    return shutil.which("pre-commit") is not None


def _clone_repo(url: str, target: Path) -> bool:
    """Clone a repo with SSH. Returns True if cloned, False if already exists."""
    if target.exists():
        print(f"  • Already exists: {target.name}")
        return False

    result = subprocess.run(
        ["git", "clone", url, str(target)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ✗ Clone failed: {target.name} — {result.stderr.strip()}")
        return False

    print(f"  ✓ Cloned: {target.name}")
    return True


def _install_hooks(repo: Path, guidelines_path: Path) -> bool:
    """Install pre-commit hooks in a repo. Returns True on success."""
    # Copy .pre-commit-config.yaml if missing
    config_src = guidelines_path / "github" / "templates" / "pre-commit-config.yaml"
    config_dest = repo / ".pre-commit-config.yaml"

    if not config_dest.exists() and config_src.exists():
        shutil.copy2(config_src, config_dest)
        print(f"    ✓ Copied .pre-commit-config.yaml")
    elif config_dest.exists():
        print(f"    • .pre-commit-config.yaml already exists")

    # Install hooks
    env = os.environ.copy()
    env["QUARK_GUIDELINES_PATH"] = str(guidelines_path)

    result = subprocess.run(
        ["pre-commit", "install"],
        cwd=str(repo), env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"    ✗ pre-commit install failed: {result.stderr.strip()}")
        return False

    result = subprocess.run(
        ["pre-commit", "install", "--hook-type", "commit-msg"],
        cwd=str(repo), env=env, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"    ✗ pre-commit install --hook-type commit-msg failed: {result.stderr.strip()}")
        return False

    print(f"    ✓ Hooks installed (pre-commit + commit-msg)")
    return True


def run(args: argparse.Namespace):
    """Execute the setup subcommand."""
    # Check pre-commit is installed
    if not _check_pre_commit():
        print("Error: pre-commit is not installed.")
        print("  Install it: pip install pre-commit")
        sys.exit(2)

    # Resolve guidelines path
    if args.guidelines:
        guidelines_path = Path(args.guidelines).resolve()
    else:
        # Auto-detect: look for this file's repo root
        guidelines_path = Path(__file__).resolve().parents[3]

    if not (guidelines_path / "github" / "templates" / "pre-commit-config.yaml").exists():
        print(f"Error: guidelines repo not found at {guidelines_path}")
        print("  Specify with --guidelines /path/to/guidelines")
        sys.exit(2)

    if args.all:
        # ─── Setup all repos ────────────────────────────────────────
        workspace = Path(args.target).resolve()
        workspace.mkdir(parents=True, exist_ok=True)

        print(f"Setting up all quarkloop repos in: {workspace}")
        print(f"Guidelines: {guidelines_path}")
        print()

        # Clone guidelines first (needed for hook installation)
        guidelines_target = workspace / "guidelines"
        _clone_repo(PRODUCT_REPOS["guidelines"], guidelines_target)
        if not guidelines_target.exists():
            guidelines_path = guidelines_target

        # Clone and set up each product repo
        for name, url in PRODUCT_REPOS.items():
            if name == "guidelines":
                continue

            target = workspace / name
            print(f"--- {name} ---")
            _clone_repo(url, target)
            if target.exists():
                _install_hooks(target, guidelines_path)
            print()

        print("Done! All repos cloned and hooks installed.")
        print()
        print("Next steps:")
        print(f"  cd {workspace}/<repo>")
        print(f"  export QUARK_GUIDELINES_PATH={guidelines_path}")
        print("  # Start coding!")

    else:
        # ─── Setup single repo ──────────────────────────────────────
        if not args.repo:
            print("Error: --repo is required (or use --all for all repos)")
            sys.exit(2)

        repo = Path(args.repo).resolve()

        if not repo.exists():
            print(f"Error: {repo} does not exist")
            sys.exit(2)

        print(f"Setting up pre-commit hooks in: {repo}")
        print(f"Guidelines: {guidelines_path}")
        print()

        # Git init if needed
        if not (repo / ".git").exists():
            result = subprocess.run(["git", "init", "-b", "main"], cwd=str(repo))
            if result.returncode != 0:
                print("Error: git init failed")
                sys.exit(2)
            print("  ✓ git init (branch: main)")

        _install_hooks(repo, guidelines_path)
        print()
        print("Done! Hooks installed.")
        print()
        print("Reminder:")
        print(f"  export QUARK_GUIDELINES_PATH={guidelines_path}")


def add_parser(subparsers) -> None:
    """Register the setup subcommand parser."""
    parser = subparsers.add_parser(
        "setup",
        help="Clone repos and install pre-commit hooks",
        description=(
            "Clone quarkloop repositories and install pre-commit hooks. "
            "Can set up a single repo (--repo) or all repos at once (--all)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Set up all repos in ~/quarkloop
  python3 tool/repo.py setup --all --target ~/quarkloop

  # Set up hooks in an existing repo
  python3 tool/repo.py setup --repo /path/to/existing-repo

  # Specify guidelines path explicitly
  python3 tool/repo.py setup --all --target ~/quarkloop --guidelines /path/to/guidelines

Prerequisites:
  pip install pre-commit
        """,
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Clone and set up all quarkloop repos",
    )
    parser.add_argument(
        "--repo", default=None,
        help="Path to an existing repo to install hooks in (use with --all for cloning)",
    )
    parser.add_argument(
        "--target", default=".",
        help="Workspace directory for --all (default: current directory)",
    )
    parser.add_argument(
        "--guidelines", default=None,
        help="Path to the guidelines repo (default: auto-detect from this tool's location)",
    )
    parser.set_defaults(func=run)
