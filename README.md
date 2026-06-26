# Quarkloop Guidelines

Unified specifications for consistent configuration across all quarkloop repositories. This repo defines the templates, section rules, and review checklists that every quarkloop repo must follow.

## Overview

Consistency across repositories reduces cognitive load for contributors and gives AI agents a predictable structure to work within. This repo contains the canonical specifications — each product repo's configuration is an instance of the templates defined here.

## Specifications

### Documentation

- [AGENTS.md Specification](./agents/SPEC.md) — the 8-section template for AI agent guides (line targets, section rules, good vs bad examples, review checklist)
- [README.md Specification](./readme/SPEC.md) — the 9-section template for repository READMEs (what goes in each section, what moves to `docs/`, review checklist)

### GitHub configuration

- [GitHub Configuration Specification](./github/SPEC.md) — issue templates, pull request template, Dependabot, EditorConfig
  - [bug_report.yml](./github/templates/bug_report.yml) — canonical bug report form
  - [feature_request.yml](./github/templates/feature_request.yml) — canonical feature request form
  - [pull_request_template.md](./github/templates/pull_request_template.md) — canonical PR template
  - [dependabot.yml](./github/templates/dependabot.yml) — canonical Dependabot config (uncomment per ecosystem)
  - [editorconfig](./github/templates/editorconfig) — canonical EditorConfig (language-aware, works for all repos)

### Linting

- [Markdown Linting Specification](./markdownlint/SPEC.md) — markdownlint rules, MDX handling, ignore patterns
  - [.markdownlint.json](./markdownlint/.markdownlint.json) — canonical markdownlint config

## Tooling

### `scripts/init_repo.py` — Scaffold a new repository

Creates the directory structure and copies canonical template files into a new (or existing) repository. Supports 4 archetypes: `library`, `platform`, `docs`, `specs`.

```bash
# Scaffold a TypeScript library
python3 scripts/init_repo.py --type library --name "Quark New Lib" --target ./quark-new-lib --language typescript

# Dry run (preview without writing)
python3 scripts/init_repo.py --type platform --name "Quark New Svc" --target ./quark-new-svc --dry-run
```

Safe to run on existing repos — it skips files that already exist.

### `scripts/validate_repo.py` — Validate a repository against specs

Checks an existing repository for compliance with the quarkloop guidelines: required files, AGENTS.md sections and line count, README.md sections and line count, GitHub config, issue templates, PR template, license.

```bash
# Validate a repo (human-readable output)
python3 scripts/validate_repo.py --repo /path/to/repo

# JSON output (for CI integration)
python3 scripts/validate_repo.py --repo /path/to/repo --json

# Quiet mode (only show failures)
python3 scripts/validate_repo.py --repo /path/to/repo --quiet
```

Exit codes: `0` = all checks passed, `1` = one or more checks failed.

## How to use

### When creating a new repo

1. Read the relevant specs.
2. Copy the template files from `github/templates/` to the new repo:
   - `.github/ISSUE_TEMPLATE/bug_report.yml`
   - `.github/ISSUE_TEMPLATE/feature_request.yml`
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/dependabot.yml` (uncomment the ecosystems that apply)
   - `.editorconfig` (rename from `editorconfig`)
   - `.markdownlint.json`
3. Create `AGENTS.md` following the [8-section template](./agents/SPEC.md).
4. Create `README.md` following the [9-section template](./readme/SPEC.md).
5. Run through the review checklists for each file before merging.

### When updating an existing repo

1. Read the relevant spec.
2. Compare your current files against the canonical templates.
3. Fill in missing files, update outdated ones.
4. Run through the review checklists before merging.

### When updating the specifications

1. Edit the spec file in this repo.
2. Open a PR describing what changed and why.
3. Once merged, each product repo should update its files to match at its own pace — no coordinated migration needed.

## Line count targets

| File | Small repos | Large repos |
|---|---|---|
| `AGENTS.md` | >= 200 lines | >= 400 lines |
| `README.md` | < 200 lines | < 200 lines |

**Rationale:** AGENTS.md should give agents better information and context — more is better as long as it's specific and enforceable. README should be an overview and entry point — shorter is better; detailed reference belongs in `docs/`.

## Structure

```
guidelines/
├── README.md                          ← this file
├── LICENSE                            ← Apache 2.0
├── agents/
│   └── SPEC.md                        ← AGENTS.md specification (8 sections)
├── readme/
│   └── SPEC.md                        ← README.md specification (9 sections)
├── github/
│   ├── SPEC.md                        ← GitHub config specification
│   └── templates/
│       ├── bug_report.yml             ← canonical bug report form
│       ├── feature_request.yml        ← canonical feature request form
│       ├── pull_request_template.md   ← canonical PR template
│       ├── dependabot.yml             ← canonical Dependabot config
│       └── editorconfig               ← canonical EditorConfig
├── markdownlint/
│   ├── SPEC.md                        ← markdown linting specification
│   └── .markdownlint.json             ← canonical markdownlint config
└── scripts/
    ├── init_repo.py                   ← scaffold a new repo from archetype
    └── validate_repo.py               ← validate a repo against specs
```

## Contributing

Pull requests are welcome. If you want to add a new specification (e.g., `ci/SPEC.md`, `security/SPEC.md`), create a new directory with a `SPEC.md` file and update this README.

By participating you agree to abide by the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.

## License

This project is licensed under the Apache License, Version 2.0 — see the [LICENSE](./LICENSE) file for details.
