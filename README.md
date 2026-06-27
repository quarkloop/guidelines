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

### `tool/repo.py` — Repository management CLI

A single entry point for all repository tooling. Six subcommands:

```bash
# Scaffold a new repository
python3 tool/repo.py init --type library --name "Quark Lib" --target ./quark-lib --language typescript

# Validate a repo and get actionable fix suggestions
python3 tool/repo.py doctor --repo /path/to/repo

# Sync canonical template files from guidelines into a repo
python3 tool/repo.py sync --repo /path/to/repo

# List all repos in a workspace and their validation status
python3 tool/repo.py list --workspace /path/to/workspace

# Validate commit message format (Conventional Commits)
python3 tool/repo.py check-commits --repo /path/to/repo

# Generate README badge markdown
python3 tool/repo.py badges --repo /path/to/repo
```

Module structure (strict SRP — one responsibility per file):

```
tool/
├── repo.py                       # Single entry point — imports cli.main()
├── src/
│   ├── cli.py                    # Argument parsing and subcommand dispatch
│   ├── generator.py              # Jinja2 template rendering (init)
│   ├── checks.py                 # Individual check functions (doctor)
│   ├── archetypes.py             # Archetype definitions (pure data)
│   ├── models.py                 # Data classes (CheckResult, ValidationReport)
│   └── commands/                 # One file per subcommand
│       ├── cmd_init.py           # `init` — scaffold new repo
│       ├── cmd_doctor.py         # `doctor` — validate + suggest fixes
│       ├── cmd_sync.py           # `sync` — copy templates from guidelines
│       ├── cmd_list.py           # `list` — org-wide validation summary
│       ├── cmd_check_commits.py  # `check-commits` — commit format validation
│       └── cmd_badges.py         # `badges` — generate README badges
└── templates/                    # Jinja2 templates (*.j2)
```

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

## Repositories

The following repositories adhere to these guidelines (26/26 doctor checks passing):

| Repository | Description | Language | License | Repo |
|---|---|---|---|---|
| **quark** | Main platform — three-service architecture (Go control plane + Java/GraalJS data plane + Go Catalog) | Java, Go, TypeScript | Apache 2.0 | [github.com/quarkloop/quark](https://github.com/quarkloop/quark) |
| **agent** | Local operating environment for autonomous AI workspaces (supervisor, runtime, plugins, services) | Go, Rust | Apache 2.0 | [github.com/quarkloop/agent](https://github.com/quarkloop/agent) |
| **quark-js** | TypeScript SDK for the Quark runtime — execute nodes, pipelines, batch, catalog | TypeScript | MIT | [github.com/quarkloop/quark-js](https://github.com/quarkloop/quark-js) |
| **docs** | Unified documentation portal — Fuma Docs (Next.js) aggregating markdown from product repos | TypeScript | Apache 2.0 | [github.com/quarkloop/docs](https://github.com/quarkloop/docs) |

This repository (`guidelines`) is a specs repo and does not fully adhere to the product-repo checks — it has no CHANGELOG, CONTRIBUTING, or SECURITY files by design.

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
└── tool/
    ├── repo.py                       ← single CLI entry point
    ├── src/
    │   ├── cli.py                    ← argument parsing and dispatch
    │   ├── generator.py              ← Jinja2 template rendering (init)
    │   ├── checks.py                 ← validation check functions (doctor)
    │   ├── archetypes.py             ← archetype definitions
    │   ├── models.py                 ← data classes
    │   └── commands/                 ← one file per subcommand
    │       ├── cmd_init.py
    │       ├── cmd_doctor.py
    │       ├── cmd_sync.py
    │       ├── cmd_list.py
    │       ├── cmd_check_commits.py
    │       └── cmd_badges.py
    └── templates/                    ← Jinja2 templates (*.j2)
```

## Contributing

Pull requests are welcome. If you want to add a new specification (e.g., `ci/SPEC.md`, `security/SPEC.md`), create a new directory with a `SPEC.md` file and update this README.

By participating you agree to abide by the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.

## License

This project is licensed under the Apache License, Version 2.0 — see the [LICENSE](./LICENSE) file for details.
