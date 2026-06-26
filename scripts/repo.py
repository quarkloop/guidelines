#!/usr/bin/env python3
"""
repo.py — Quarkloop repository management CLI.

This is the single entry point for all repository tooling in the quarkloop
organization. It provides two subcommands:

  init      Scaffold a new repository with the standard file layout,
            GitHub configuration, and documentation skeletons. Supports
            four archetypes: library, platform, docs, specs.

  validate  Check an existing repository against the quarkloop guidelines.
            Verifies required files, AGENTS.md structure and line count,
            README.md structure and line count, GitHub config presence,
            issue/PR template fields, and license type.

USAGE

  Scaffolding a new repo:

      python3 scripts/repo.py init \\
          --type library \\
          --name "Quark JS SDK" \\
          --target ./quark-js \\
          --repo-name quark-js \\
          --language typescript

      # Dry run (preview without writing):
      python3 scripts/repo.py init --type platform --name "Quark" --target ./quark --dry-run

  Validating an existing repo:

      python3 scripts/repo.py validate --repo /path/to/repo

      # JSON output for CI/CD:
      python3 scripts/repo.py validate --repo /path/to/repo --json

      # Quiet mode (only show failures):
      python3 scripts/repo.py validate --repo /path/to/repo --quiet

  Help:

      python3 scripts/repo.py --help
      python3 scripts/repo.py init --help
      python3 scripts/repo.py validate --help

EXIT CODES

  0  Success (init completed, or all validation checks passed)
  1  One or more validation checks failed
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

  This file is a thin entry point. All logic lives in scripts/src/:

    src/cli.py        Argument parsing and subcommand dispatch
    src/generator.py  Jinja2 template rendering and file writing (init)
    src/validator.py  Check orchestration and report assembly (validate)
    src/checks.py     Individual validation check functions
    src/archetypes.py Archetype definitions (pure data)
    src/models.py     Data classes (CheckResult, ValidationReport)

  Jinja2 templates live in scripts/templates/ (*.j2 files).
  Static template files (editorconfig, issue forms) are copied from
  github/templates/ and markdownlint/.

SEE ALSO

  https://github.com/quarkloop/guidelines — full specifications
"""

import sys
import os

# Add scripts/ to sys.path so we can import the src package.
# This allows the script to be run from any directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()
