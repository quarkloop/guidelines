#!/usr/bin/env python3
"""
setup_standalone.py — Bootstrap script for quarkloop development environment.

This is a STANDALONE script — it does NOT require the guidelines repo to
be cloned first. It clones all quarkloop repos and installs pre-commit
hooks in one command.

After running this, the full guidelines tool (tool/repo.py) is available
at <target>/guidelines/tool/repo.py for doctor, sync, list, etc.

Usage:
  # Clone all repos + install hooks
  python3 setup_standalone.py --all --target ~/quarkloop

  # Install hooks in an existing repo
  python3 setup_standalone.py --repo /path/to/existing-repo

  # Or via curl (no download needed):
  curl -fsSL https://raw.githubusercontent.com/quarkloop/guidelines/main/tool/setup_standalone.py | python3 - --all --target ~/quarkloop

Prerequisites:
  pip install pre-commit

The pre-commit config is embedded in this script — no file dependencies.
After cloning, the guidelines repo's canonical .pre-commit-config.yaml
takes over (the embedded version is just for bootstrap).
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ─── Product repos ──────────────────────────────────────────────────────

PRODUCT_REPOS = {
    "quark": "git@github.com:quarkloop/quark.git",
    "agent": "git@github.com:quarkloop/agent.git",
    "quark-js": "git@github.com:quarkloop/quark-js.git",
    "docs": "git@github.com:quarkloop/docs.git",
    "guidelines": "git@github.com:quarkloop/guidelines.git",
}

# ─── Embedded pre-commit config ────────────────────────────────────────
# This is the bootstrap version. After cloning, the guidelines repo's
# canonical .pre-commit-config.yaml at github/templates/ is the source
# of truth. This embedded version ensures hooks work immediately after
# clone, even before the developer reads any docs.

PRE_COMMIT_CONFIG = """\
# Pre-commit hooks for quarkloop repositories.
# After cloning the guidelines repo, run `python3 tool/repo.py sync` to
# get the canonical version with all hooks up to date.
#
# Set QUARK_GUIDELINES_PATH to your guidelines checkout:
#   export QUARK_GUIDELINES_PATH=<workspace>/guidelines

repos:
  # ─── Quarkloop guidelines checks ──────────────────────────────────
  - repo: local
    hooks:
      - id: quark-check-commits
        name: "quarkloop: commit message format"
        entry: bash -c 'python3 "$QUARK_GUIDELINES_PATH/tool/repo.py" check-commits --repo . --count 1'
        language: system
        stages: [commit-msg]
        always_run: true

      - id: quark-doctor
        name: "quarkloop: repo doctor"
        entry: bash -c 'python3 "$QUARK_GUIDELINES_PATH/tool/repo.py" doctor --repo . --quiet'
        language: system
        always_run: true
        pass_filenames: false

  # ─── Standard hooks ───────────────────────────────────────────────
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
        exclude: '\\.md$'
      - id: end-of-file-fixer
        exclude: '\\.md$'
      - id: check-yaml
        exclude: '\\.github/ISSUE_TEMPLATE/.*\\.yml$'
      - id: check-json
        exclude: '(package-lock\\.json|skills-lock\\.json|\\.source/.*)'
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: check-added-large-files
        args: ['--maxkb=500']
"""


# ─── Helper functions ──────────────────────────────────────────────────

def check_pre_commit() -> bool:
    """Check if pre-commit is installed."""
    return shutil.which("pre-commit") is not None


def clone_repo(url: str, target: Path) -> bool:
    """Clone a repo. Returns True if cloned, False if already exists."""
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


def install_hooks(repo: Path, guidelines_path: Path) -> bool:
    """Install pre-commit hooks in a repo. Returns True on success."""
    # Write .pre-commit-config.yaml if missing
    config_dest = repo / ".pre-commit-config.yaml"
    if not config_dest.exists():
        config_dest.write_text(PRE_COMMIT_CONFIG)
        print(f"    ✓ Created .pre-commit-config.yaml")
    else:
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
        print(f"    ✗ commit-msg hook install failed: {result.stderr.strip()}")
        return False

    print(f"    ✓ Hooks installed (pre-commit + commit-msg)")
    return True


# ─── Main ──────────────────────────────────────────────────────────────

def cmd_all(args):
    """Clone all repos and install hooks."""
    workspace = Path(args.target).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    print(f"Cloning all quarkloop repos into: {workspace}")
    print()

    # Clone guidelines first (needed for hook installation)
    guidelines_target = workspace / "guidelines"
    clone_repo(PRODUCT_REPOS["guidelines"], guidelines_target)

    if not guidelines_target.exists():
        print(f"\nError: Failed to clone guidelines repo — cannot install hooks.")
        sys.exit(1)

    guidelines_path = guidelines_target

    # Clone and set up each product repo
    for name, url in PRODUCT_REPOS.items():
        if name == "guidelines":
            continue

        target = workspace / name
        print(f"--- {name} ---")
        clone_repo(url, target)
        if target.exists():
            install_hooks(target, guidelines_path)
        print()

    print("=" * 50)
    print("Done! All repos cloned and hooks installed.")
    print()
    print("Next steps:")
    print(f"  cd {workspace}/<repo>")
    print(f"  export QUARK_GUIDELINES_PATH={guidelines_path}")
    print()
    print("Available commands:")
    print(f"  python3 {guidelines_path}/tool/repo.py doctor --repo .")
    print(f"  python3 {guidelines_path}/tool/repo.py sync --repo .")
    print(f"  python3 {guidelines_path}/tool/repo.py list --workspace {workspace}")


def cmd_single(args):
    """Install hooks in a single existing repo."""
    repo = Path(args.repo).resolve()

    if not repo.exists():
        print(f"Error: {repo} does not exist")
        sys.exit(2)

    # Try to find guidelines repo
    if args.guidelines:
        guidelines_path = Path(args.guidelines).resolve()
    else:
        # Search sibling directories
        parent = repo.parent
        guidelines_path = parent / "guidelines"
        if not guidelines_path.exists():
            # Search parent's parent
            guidelines_path = repo.parent.parent / "guidelines"

    if not guidelines_path.exists():
        print(f"Error: guidelines repo not found.")
        print(f"  Searched: {guidelines_path}")
        print(f"  Specify with --guidelines /path/to/guidelines")
        sys.exit(2)

    print(f"Installing hooks in: {repo}")
    print(f"Guidelines: {guidelines_path}")
    print()

    # Git init if needed
    if not (repo / ".git").exists():
        subprocess.run(["git", "init", "-b", "main"], cwd=str(repo))
        print("  ✓ git init (branch: main)")

    install_hooks(repo, guidelines_path)
    print()
    print("Done! Hooks installed.")
    print()
    print("Reminder:")
    print(f"  export QUARK_GUIDELINES_PATH={guidelines_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap quarkloop development environment — clone repos and install pre-commit hooks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clone all repos into ~/quarkloop + install hooks
  python3 setup_standalone.py --all --target ~/quarkloop

  # Install hooks in an existing repo
  python3 setup_standalone.py --repo /path/to/existing-repo

  # Via curl (no download needed):
  curl -fsSL https://raw.githubusercontent.com/quarkloop/guidelines/main/tool/setup_standalone.py | python3 - --all --target ~/quarkloop

Prerequisites:
  pip install pre-commit
        """,
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Clone all quarkloop repos and install hooks",
    )
    parser.add_argument(
        "--repo", default=None,
        help="Path to an existing repo to install hooks in",
    )
    parser.add_argument(
        "--target", default=".",
        help="Workspace directory for --all (default: current directory)",
    )
    parser.add_argument(
        "--guidelines", default=None,
        help="Path to guidelines repo (for --repo mode, default: auto-detect)",
    )

    args = parser.parse_args()

    if not check_pre_commit():
        print("Error: pre-commit is not installed.")
        print("  Install it: pip install pre-commit")
        sys.exit(2)

    if args.all:
        cmd_all(args)
    elif args.repo:
        cmd_single(args)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
