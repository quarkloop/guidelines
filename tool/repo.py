#!/usr/bin/env python3
"""
repo.py — Quarkloop repository management CLI.

This is the single entry point for all repository tooling in the quarkloop
organization. It provides seven subcommands:

  init      Scaffold a new repository with the standard file layout,
            GitHub configuration, and documentation skeletons. Supports
            four archetypes: library, platform, docs, specs.

  doctor    Validate an existing repository against the quarkloop
            guidelines and report failures with actionable fix
            suggestions.

  sync      Copy canonical template files from the guidelines repo into
            an existing repo, overwriting outdated copies.

  list      Discover all git repositories in a workspace directory, run
            guideline checks on each, and print a summary table.

  check-commits
            Validate recent commit messages against the Conventional
            Commits format.

  badges    Generate consistent README badge markdown for a repository.

  setup     Clone quarkloop repositories and install pre-commit hooks.
            Can set up a single repo (--repo) or all repos at once
            (--all).

USAGE

  Scaffolding a new repo:

      python3 tool/repo.py init \\
          --type library \\
          --name "Quark JS SDK" \\
          --target ./quark-js \\
          --repo-name quark-js \\
          --language typescript

  Diagnosing an existing repo:

      python3 tool/repo.py doctor --repo /path/to/repo

      # JSON output for CI/CD:
      python3 tool/repo.py doctor --repo /path/to/repo --json

      # Quiet mode (only show failures and fix suggestions):
      python3 tool/repo.py doctor --repo /path/to/repo --quiet

  Syncing template files from guidelines:

      python3 tool/repo.py sync --repo /path/to/repo

      # Sync specific files only:
      python3 tool/repo.py sync --repo /path/to/repo --files .editorconfig,.markdownlint.json

  Listing all repos in a workspace:

      python3 tool/repo.py list --workspace /path/to/workspace

  Checking commit messages:

      python3 tool/repo.py check-commits --repo /path/to/repo
      python3 tool/repo.py check-commits --repo /path/to/repo --count 20
      python3 tool/repo.py check-commits --repo /path/to/repo --range main..feature-branch

  Generating README badges:

      python3 tool/repo.py badges --repo /path/to/repo
      python3 tool/repo.py badges --repo /path/to/repo --no-ci

  Cloning repos and installing pre-commit hooks:

      python3 tool/repo.py setup --all --target ~/quarkloop
      python3 tool/repo.py setup --repo /path/to/existing-repo

  Help:

      python3 tool/repo.py --help
      python3 tool/repo.py <command> --help

EXIT CODES

  0  Success (init completed, all checks passed, or all commits valid)
  1  One or more checks failed (doctor) or invalid commits found (check-commits)
  2  Invalid arguments or repository path not found

ARCHETYPES

  library   Single-language library (TypeScript, Go, Rust, Java).
            Creates: src/, docs/, examples/, package.json or go.mod, etc.

  platform  Multi-language platform (Go + Java + Rust, etc.).
            Creates: docs/, deploy/, scripts/, proto/, e2e/, Makefile, go.work

  docs      Documentation site (Next.js / Fuma Docs).
            Creates: app/, components/, lib/, scripts/, content/, public/

  specs     Specifications repository (like this guidelines repo).
            Creates: .github/ only — content is SPEC.md files you author

MODULE LAYOUT

  This file is a thin entry point. All logic lives in tool/src/:

    src/cli.py             Argument parsing and subcommand dispatch
    src/generator.py       Jinja2 template rendering and file writing (init)
    src/checks.py          Individual validation check functions (doctor)
    src/archetypes.py      Archetype definitions (pure data)
    src/models.py          Data classes (CheckResult, ValidationReport)
    src/commands/
      cmd_init.py          `init` subcommand
      cmd_doctor.py        `doctor` subcommand (merged validate + doctor)
      cmd_sync.py          `sync` subcommand
      cmd_list.py          `list` subcommand
      cmd_check_commits.py `check-commits` subcommand
      cmd_badges.py        `badges` subcommand
      cmd_setup.py         `setup` subcommand

  Jinja2 templates live in tool/templates/ (*.j2 files).
  Static template files (editorconfig, issue forms) are copied from
  github/templates/ and markdownlint/.

SEE ALSO

  https://github.com/quarkloop/guidelines — full specifications
"""

import sys
import os

# Add tool/ to sys.path so we can import the src package.
# This allows the script to be run from any directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()
