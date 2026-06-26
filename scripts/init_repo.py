#!/usr/bin/env python3
"""
init_repo.py — Scaffold a new quarkloop repository with required files.

Creates the directory structure and copies canonical template files from
the guidelines repo into a new (or existing) repository directory.

Usage:
  python3 scripts/init_repo.py --type library --name quark-new-lib --target ./quark-new-lib
  python3 scripts/init_repo.py --type platform --name quark-new-svc --target ./quark-new-svc
  python3 scripts/init_repo.py --type docs --name quark-new-docs --target ./quark-new-docs
  python3 scripts/init_repo.py --type specs --name quark-new-specs --target ./quark-new-specs

Archetypes:
  library   — single-language library (like quark-js): src/, docs/, package.json
  platform  — multi-language platform (like quark): components, Makefile, go.work
  docs      — documentation site (like docs): app/, components/, next.config.mjs
  specs     — specifications repo (like guidelines): topic/SPEC.md structure

The script does NOT overwrite existing files — it skips them with a warning.
This makes it safe to run on an existing repo to fill in missing files.
"""

import argparse
import shutil
import sys
from pathlib import Path


# ─── Archetype definitions ──────────────────────────────────────────────

ARCHETYPES = {
    "library": {
        "description": "Single-language library (TypeScript, Go, Rust, or Java)",
        "directories": ["src", "docs", "examples", ".github/ISSUE_TEMPLATE"],
        "files": {
            # GitHub config
            ".github/ISSUE_TEMPLATE/bug_report.yml": "github/templates/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml": "github/templates/feature_request.yml",
            ".github/PULL_REQUEST_TEMPLATE.md": None,  # generated
            ".github/dependabot.yml": None,  # generated
            # Editor / linting
            ".editorconfig": "github/templates/editorconfig",
            ".markdownlint.json": "markdownlint/.markdownlint.json",
            ".markdownlintignore": None,  # generated
            # Standard files
            "AGENTS.md": None,  # generated
            "CHANGELOG.md": None,  # generated
            "CODE_OF_CONDUCT.md": None,  # generated (Contributor Covenant)
            "CONTRIBUTING.md": None,  # generated
            "LICENSE": None,  # copy from guidelines root
            "README.md": None,  # generated
            "SECURITY.md": None,  # generated
            ".gitignore": None,  # generated
        },
    },
    "platform": {
        "description": "Multi-language platform (Go + Java + Rust, etc.)",
        "directories": [
            "docs",
            "deploy",
            "scripts",
            "proto",
            "e2e",
            ".github/ISSUE_TEMPLATE",
        ],
        "files": {
            # GitHub config
            ".github/ISSUE_TEMPLATE/bug_report.yml": "github/templates/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml": "github/templates/feature_request.yml",
            ".github/PULL_REQUEST_TEMPLATE.md": None,
            ".github/dependabot.yml": None,
            # Editor / linting
            ".editorconfig": "github/templates/editorconfig",
            ".markdownlint.json": "markdownlint/.markdownlint.json",
            ".markdownlintignore": None,
            # Standard files
            "AGENTS.md": None,
            "CHANGELOG.md": None,
            "CODE_OF_CONDUCT.md": None,
            "CONTRIBUTING.md": None,
            "LICENSE": None,
            "README.md": None,
            "SECURITY.md": None,
            ".gitignore": None,
        },
    },
    "docs": {
        "description": "Documentation site (Next.js / Fuma Docs)",
        "directories": [
            "app",
            "components",
            "lib",
            "scripts",
            "content",
            "public",
            ".github/ISSUE_TEMPLATE",
        ],
        "files": {
            # GitHub config
            ".github/ISSUE_TEMPLATE/bug_report.yml": "github/templates/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml": "github/templates/feature_request.yml",
            ".github/PULL_REQUEST_TEMPLATE.md": None,
            ".github/dependabot.yml": None,
            # Editor / linting
            ".editorconfig": "github/templates/editorconfig",
            ".markdownlint.json": "markdownlint/.markdownlint.json",
            ".markdownlintignore": None,
            # Standard files
            "AGENTS.md": None,
            "LICENSE": None,
            "README.md": None,
            ".gitignore": None,
        },
    },
    "specs": {
        "description": "Specifications repository (like guidelines)",
        "directories": [".github/ISSUE_TEMPLATE"],
        "files": {
            # GitHub config
            ".github/ISSUE_TEMPLATE/bug_report.yml": "github/templates/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml": "github/templates/feature_request.yml",
            ".github/PULL_REQUEST_TEMPLATE.md": None,
            ".github/dependabot.yml": None,
            # Editor / linting
            ".editorconfig": "github/templates/editorconfig",
            ".markdownlint.json": "markdownlint/.markdownlint.json",
            # Standard files
            "AGENTS.md": None,
            "LICENSE": None,
            "README.md": None,
            ".gitignore": None,
        },
    },
}


# ─── Generated file templates ───────────────────────────────────────────

LICENSE_APACHE = """\
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      [Full Apache 2.0 license text — see guidelines/LICENSE for the
      complete version. This placeholder is replaced at runtime.]

   Copyright 2026 Quarkloop Contributors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied. See the License for the specific language governing
   permissions and limitations under the License.
"""

CODE_OF_CONDUCT = """\
# Contributor Covenant Code of Conduct

## Our pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

[Full Contributor Covenant v2.0 text — see
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html
for the complete version.]
"""

CHANGELOG_TEMPLATE = """\
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial repository setup.

## [0.1.0] - YYYY-MM-DD

### Added

- Initial release.
"""

CONTRIBUTING_TEMPLATE = """\
# Contributing to {name}

Thank you for your interest in contributing! This guide covers everything you need to get started.

## Prerequisites

- [List language-specific prerequisites here]

## Getting started

```bash
git clone https://github.com/quarkloop/{repo_name}
cd {repo_name}
# [Add build/install commands here]
```

## Running tests

```bash
# [Add test commands here]
```

## Code style

- Follow the existing code style in the repository
- Run the formatter before committing
- Exported types and functions require doc comments

## Submitting changes

1. Fork the repository and create a branch from `main`
2. Make your changes — keep commits focused and atomic
3. Run the test suite
4. Open a pull request against `main` with a clear description of what and why
5. Link any related issues

### Commit message format

```
type(scope): short summary

Optional longer description explaining why the change was made.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

## Reporting bugs

Please use GitHub Issues with the bug report template. Include your project version, runtime version, OS, and steps to reproduce.

## Code of Conduct

By participating in this project you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
"""

SECURITY_TEMPLATE = """\
# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| main    | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

**Do NOT file a public GitHub issue for security vulnerabilities.**

Instead, email **reza.ebrahimi.dev@gmail.com** with:

1. A description of the vulnerability and its impact.
2. Steps to reproduce (a minimal reproducer is ideal).
3. Affected component and version.
4. Any suggested fixes or mitigations.

You should receive an acknowledgment within 72 hours.

## Scope

In scope:
- [List in-scope components here]

Out of scope:
- Vulnerabilities in third-party dependencies (report upstream)
- Social engineering attacks
- Theoretical timing attacks without a demonstrated exploit
"""

README_TEMPLATE = """\
# {name}

[One-sentence tagline describing what this is]

## Overview

[2-3 sentences. What this is, who it's for, what problem it solves.]

## Features

- [Feature 1]
- [Feature 2]
- [Feature 3]
- [Feature 4]

## Installation

```bash
# [Install commands]
```

## Quick start

```bash
# [Minimal end-to-end example]
```

## Documentation

- [Architecture](./docs/architecture.mdx) — [description]
- [API reference](./docs/api.mdx) — [description]
- [Build & development](./docs/build.mdx) — [description]
- [Changelog](./CHANGELOG.md) — release history
- [Contributing](./CONTRIBUTING.md) — development setup, PR workflow, code style

## Compatibility

| Component | Language | Version |
|---|---|---|
| [Component] | [Language] | [Version] |

## Contributing

Pull requests are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, commit message conventions, and code style rules. By participating you agree to abide by the [Code of Conduct](./CODE_OF_CONDUCT.md).

## License

This project is licensed under the Apache License, Version 2.0 — see the [LICENSE](./LICENSE) file for details.
"""

AGENTS_TEMPLATE = """\
# Agent Guide

[One-sentence statement of what this repo is and what an AI agent's job is here.]

## Repository

- **Name**: {name}
- **Language**: [primary language(s)]
- **License**: Apache 2.0
- **Repo**: [github.com/quarkloop/{repo_name}]
- **Guidelines**: [quarkloop/guidelines](https://github.com/quarkloop/guidelines)

## Quick reference

```bash
# [Build command]
# [Test command]
# [Check command]
```

## Structure

```
[repo layout tree]
```

## Rules

1. [Rule 1]
2. [Rule 2]
3. [Rule 3]
4. Run [check command] before every commit.
5. Do not [common mistake].

## Boundaries

- [Component A] owns [responsibility].
- [Component B] owns [responsibility].

## Commit conventions

- Format: `type(scope): short summary`
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `build`
- One scope per commit.
- Inspect staged files before every commit.
- Never stage: `.env`, `node_modules/`, `dist/`, editor configs.

## Testing

- Every new function needs a unit test.
- Every bug fix needs a regression test.
- Run [test command] — must pass with zero failures.

## When you're stuck

- Read [docs link] for design rationale.
- Read the [AGENTS.md spec](https://github.com/quarkloop/guidelines/blob/main/agents/SPEC.md) for org-wide conventions.
- Search existing issues and PRs before asking.
"""

PR_TEMPLATE = """\
## Description

<!-- What does this PR do and why? Link related issues with "Closes #N". -->

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor
- [ ] Documentation
- [ ] Chore / dependency update

## Checklist

- [ ] Code builds without errors
- [ ] Tests pass with zero failures
- [ ] No new linting warnings introduced
- [ ] Documentation updated (README, AGENTS.md, code comments) where relevant
- [ ] Changes are scoped — no unrelated files in this PR
"""

DEPENDABOT_TEMPLATE_NPM = """\
version: 2

updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 10
    groups:
      minor-and-patch:
        update-types:
          - minor
          - patch
    labels:
      - dependencies

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 10
    labels:
      - dependencies
"""

DEPENDABOT_TEMPLATE_GOMOD = """\
version: 2

updates:
  - package-ecosystem: gomod
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 10
    groups:
      minor-and-patch:
        update-types:
          - minor
          - patch
    labels:
      - dependencies

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 10
    labels:
      - dependencies
"""

GITIGNORE_LIBRARY = """\
# Dependencies
node_modules/

# Build output
dist/
*.tsbuildinfo

# Editor / OS
.DS_Store
*.swp
.vscode/
.idea/

# Environment
.env
.env.local
"""

GITIGNORE_PLATFORM = """\
# Build output
bin/
dist/
target/
*.out
*.test
*.prof

# Go
vendor/

# Rust
target/

# Java
*.class
target/

# Editor / OS
.DS_Store
*.swp
.vscode/
.idea/

# Environment
.env
.env.local
"""

GITIGNORE_DOCS = """\
# Dependencies
node_modules/

# Next.js build output
.next/
out/

# Vercel
.vercel/

# Content is synced from product repos — do not commit
content/

# Pagefind index (generated at build time)
public/pagefind/

# Fuma Docs generated source
.source/

# OS / editor
.DS_Store
*.swp
.vscode/
.idea/

# Environment
.env
.env.local

# TypeScript
*.tsbuildinfo
next-env.d.ts
"""

MARKDOWNLINTIGNORE_LIBRARY = """\
node_modules/
dist/
.next/
.vercel/
bun.lock
"""

MARKDOWNLINTIGNORE_PLATFORM = """\
node_modules/
bin/
vendor/
target/
dist/
.next/
.vercel/
e2e/testdata/
"""

MARKDOWNLINTIGNORE_DOCS = """\
node_modules/
.next/
.vercel/
.source/
content/
public/pagefind/
package-lock.json
"""


# ─── Helper functions ───────────────────────────────────────────────────

def create_directory(target: Path, dir_path: str, dry_run: bool = False) -> bool:
    """Create a directory (with parents). Returns True if created, False if existed."""
    full = target / dir_path
    if full.exists():
        return False
    if not dry_run:
        full.mkdir(parents=True, exist_ok=True)
    return True


def copy_template(
    guidelines_root: Path,
    target: Path,
    dest: str,
    source: str,
    dry_run: bool = False,
) -> bool:
    """Copy a template file from the guidelines repo. Returns True if copied, False if existed."""
    dest_path = target / dest
    if dest_path.exists():
        return False
    src_path = guidelines_root / source
    if not src_path.exists():
        print(f"  ⚠ Source not found: {source}")
        return False
    if not dry_run:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)
    return True


def write_generated(
    target: Path,
    dest: str,
    content: str,
    dry_run: bool = False,
) -> bool:
    """Write a generated file. Returns True if written, False if existed."""
    dest_path = target / dest
    if dest_path.exists():
        return False
    if not dry_run:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content)
    return True


# ─── Main ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new quarkloop repository with required files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Archetypes:
  library   — single-language library (like quark-js)
  platform  — multi-language platform (like quark)
  docs      — documentation site (like docs)
  specs     — specifications repository (like guidelines)

Examples:
  python3 scripts/init_repo.py --type library --name quark-new-lib --target ./quark-new-lib
  python3 scripts/init_repo.py --type platform --name quark-new-svc --target ./quark-new-svc --dry-run
        """,
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=ARCHETYPES.keys(),
        help="Repository archetype",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Human-readable project name (e.g., 'Quark New Lib')",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target directory (will be created if it doesn't exist)",
    )
    parser.add_argument(
        "--repo-name",
        default=None,
        help="GitHub repo name (e.g., 'quark-new-lib'). Defaults to --target basename.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without writing files",
    )
    parser.add_argument(
        "--language",
        default=None,
        choices=["typescript", "go", "rust", "java", "mixed"],
        help="Primary language (affects .gitignore and dependabot config)",
    )

    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).resolve().parent
    guidelines_root = script_dir.parent  # scripts/ is one level down from repo root
    target = Path(args.target).resolve()
    repo_name = args.repo_name or target.name

    archetype = ARCHETYPES[args.type]
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Scaffolding {args.type} repo: {args.name}")
    print(f"  Target: {target}")
    print(f"  Repo name: {repo_name}")
    print(f"  Language: {args.language or 'unspecified'}")
    print()

    # Create target directory
    if not target.exists():
        if not args.dry_run:
            target.mkdir(parents=True)
        print(f"  ✓ Created target directory: {target}")
    else:
        print(f"  • Target directory exists: {target}")

    # Create directories
    print()
    print("Directories:")
    for dir_path in archetype["directories"]:
        created = create_directory(target, dir_path, args.dry_run)
        status = "✓ Created" if created else "• Exists"
        print(f"  {status}: {dir_path}/")

    # Determine language-specific templates
    language = args.language or ""
    if args.type == "library":
        if language == "typescript":
            dependabot_content = DEPENDABOT_TEMPLATE_NPM
            gitignore_content = GITIGNORE_LIBRARY
            markdownlintignore_content = MARKDOWNLINTIGNORE_LIBRARY
        elif language == "go":
            dependabot_content = DEPENDABOT_TEMPLATE_GOMOD
            gitignore_content = GITIGNORE_PLATFORM
            markdownlintignore_content = MARKDOWNLINTIGNORE_PLATFORM
        else:
            dependabot_content = DEPENDABOT_TEMPLATE_NPM
            gitignore_content = GITIGNORE_LIBRARY
            markdownlintignore_content = MARKDOWNLINTIGNORE_LIBRARY
    elif args.type == "platform":
        dependabot_content = DEPENDABOT_TEMPLATE_GOMOD
        gitignore_content = GITIGNORE_PLATFORM
        markdownlintignore_content = MARKDOWNLINTIGNORE_PLATFORM
    elif args.type == "docs":
        dependabot_content = DEPENDABOT_TEMPLATE_NPM
        gitignore_content = GITIGNORE_DOCS
        markdownlintignore_content = MARKDOWNLINTIGNORE_DOCS
    else:  # specs
        dependabot_content = DEPENDABOT_TEMPLATE_NPM
        gitignore_content = GITIGNORE_LIBRARY
        markdownlintignore_content = ""

    # Process files
    print()
    print("Files:")
    created_count = 0
    skipped_count = 0

    for dest, source in archetype["files"].items():
        if source is not None:
            # Copy from template
            created = copy_template(guidelines_root, target, dest, source, args.dry_run)
        else:
            # Generate from template string
            content = None
            if dest == "LICENSE":
                # Copy full Apache 2.0 from guidelines root
                license_src = guidelines_root / "LICENSE"
                if license_src.exists():
                    created = copy_template(guidelines_root, target, dest, "LICENSE", args.dry_run)
                else:
                    content = LICENSE_APACHE
                    created = write_generated(target, dest, content, args.dry_run)
            elif dest == "AGENTS.md":
                content = AGENTS_TEMPLATE.format(name=args.name, repo_name=repo_name)
                created = write_generated(target, dest, content, args.dry_run)
            elif dest == "README.md":
                content = README_TEMPLATE.format(name=args.name, repo_name=repo_name)
                created = write_generated(target, dest, content, args.dry_run)
            elif dest == "CONTRIBUTING.md":
                content = CONTRIBUTING_TEMPLATE.format(name=args.name, repo_name=repo_name)
                created = write_generated(target, dest, content, args.dry_run)
            elif dest == "SECURITY.md":
                created = write_generated(target, dest, SECURITY_TEMPLATE, args.dry_run)
            elif dest == "CHANGELOG.md":
                created = write_generated(target, dest, CHANGELOG_TEMPLATE, args.dry_run)
            elif dest == "CODE_OF_CONDUCT.md":
                created = write_generated(target, dest, CODE_OF_CONDUCT, args.dry_run)
            elif dest == ".github/PULL_REQUEST_TEMPLATE.md":
                created = write_generated(target, dest, PR_TEMPLATE, args.dry_run)
            elif dest == ".github/dependabot.yml":
                created = write_generated(target, dest, dependabot_content, args.dry_run)
            elif dest == ".gitignore":
                created = write_generated(target, dest, gitignore_content, args.dry_run)
            elif dest == ".markdownlintignore":
                if markdownlintignore_content:
                    created = write_generated(target, dest, markdownlintignore_content, args.dry_run)
                else:
                    continue  # skip for archetypes that don't need it
            else:
                print(f"  ⚠ Unknown generated file: {dest}")
                continue

        if created:
            print(f"  ✓ Created: {dest}")
            created_count += 1
        else:
            print(f"  • Exists:  {dest}")
            skipped_count += 1

    # Summary
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


if __name__ == "__main__":
    main()
