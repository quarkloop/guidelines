# GitHub Configuration Specification

This document defines the unified GitHub configuration for all quarkloop repositories: issue templates, pull request template, Dependabot configuration, and EditorConfig.

## Purpose

Consistent GitHub configuration across repositories:

- Gives contributors a predictable experience when filing issues or opening PRs
- Ensures dependency security updates are automated everywhere
- Enforces editor consistency (tabs vs spaces, line endings, final newline) across all repos and all contributors

## Required files

Every repository must have:

| File | Purpose |
|---|---|
| `.github/ISSUE_TEMPLATE/bug_report.yml` | Structured bug report form |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | Structured feature request form |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR description template with checklist |
| `.github/dependabot.yml` | Automated dependency update PRs |
| `.editorconfig` | Editor consistency (tabs, spaces, line endings) |
| `.pre-commit-config.yaml` | Pre-commit hooks (commit format + repo checks + standard hygiene) |

### Pre-commit

Every repo must have a `.pre-commit-config.yaml` that:

1. **Enforces commit message format** — runs `check-commits` on every commit
2. **Checks repo health** — runs `doctor --quiet` on every commit (fails on missing files, broken AGENTS.md/README.md structure)
3. **Standard hygiene** — trailing whitespace, end-of-file fixer, YAML/JSON validation, large file prevention, merge conflict detection

The canonical config is at `github/templates/pre-commit-config.yaml`. Each repo copies it and sets the `QUARK_GUIDELINES_PATH` environment variable to point to the local guidelines checkout.

**Setup (one-time per repo):**
```bash
pip install pre-commit
cp <guidelines-repo>/github/templates/pre-commit-config.yaml .pre-commit-config.yaml
export QUARK_GUIDELINES_PATH=/path/to/guidelines
pre-commit install
pre-commit install --hook-type commit-msg
```

**Run manually:**
```bash
pre-commit run --all-files                        # all file-level hooks
pre-commit run --all-files --hook-stage commit-msg # commit message hook
```

**Note:** Pre-commit checks the current commit being made, NOT all commit history. To check historical commits, use `check-commits` with `--count` or `--range` directly.

---

## Issue templates

### `bug_report.yml`

Uses GitHub's issue form schema (YAML). Every repo uses the same 7-field structure:

1. **Description** — what went wrong
2. **Steps to reproduce** — numbered list
3. **Expected behaviour** — what should have happened
4. **Actual behaviour** — what actually happened
5. **Version** — the project version (repo-specific: `quark version`, `npm ls @quarkloop/quark-js`, etc.)
6. **Runtime version** — language runtime (repo-specific: Go, Node, Java, etc.)
7. **Operating system** — OS name and version

The canonical template is at `github/templates/bug_report.yml`. Each repo adapts the `version` and `runtime-version` fields:

| Repo | Version field | Runtime field |
|---|---|---|
| `quark` | `quark version` | Go version + Java version |
| `quark-js` | `npm ls @quarkloop/quark-js` | Bun / Node / Deno version |
| `agent` | `quark version` | Go version |
| `docs` | (commit SHA) | Node version |

### `feature_request.yml`

Three fields:

1. **Problem** — what problem does this feature solve
2. **Proposed solution** — what you want to happen
3. **Alternatives considered** — any other solutions you've considered

The canonical template is at `github/templates/feature_request.yml`. This is identical across all repos — no adaptation needed.

---

## Pull request template

### `.github/PULL_REQUEST_TEMPLATE.md`

Every repo uses the same 3-section structure:

1. **Description** — what the PR does and why, with `Closes #N` for linked issues
2. **Type of change** — checkboxes: Bug fix, New feature, Refactor, Documentation, Chore/dependency update
3. **Checklist** — pre-merge verification items

The checklist items are adapted per repo:

| Repo | Checklist items |
|---|---|
| `quark` | `make vet`, `make test`, `make arch-check`, `make dead-code-check` |
| `quark-js` | `bun run typecheck`, E2E test passes |
| `agent` | `make vet`, `make test`, `make arch-check`, `make dead-code-check`, boundary rules |
| `docs` | `npm run build` passes, `content/` not committed |
| `guidelines` | markdown linting passes |

The canonical template is at `github/templates/pull_request_template.md`. Each repo copies it and adapts the checklist.

---

## Dependabot configuration

### `.github/dependabot.yml`

Dependabot opens automated PRs when dependencies are outdated. Every repo with dependencies must have this file.

### Configuration rules

- **Schedule**: weekly (`interval: weekly`, `day: monday`)
- **Grouping**: group minor and patch updates together (one PR per ecosystem); major updates get individual PRs
- **Open PR limit**: 10 per ecosystem
- **Reviewers**: none by default (add per-repo if desired)
- **Labels**: `dependencies` (plus the repo's default label set)

### Per-ecosystem configuration

| Ecosystem | Applies to | Directory |
|---|---|---|
| `npm` | quark-js, docs, agent (web/) | `/` (root) or `/web` |
| `go-modules` | agent, quark | `/` (root) |
| `maven` | quark | `/` (root) |
| `cargo` | agent (harness) | `/services/harness` |
| `github-actions` | all repos with workflows | `/` (root) |

### Grouping rules

Minor and patch updates are grouped (one PR per ecosystem per week). Major updates (`major`) are NOT grouped — each gets its own PR so they can be reviewed individually.

```yaml
groups:
  minor-and-patch:
    update-types:
      - "minor"
      - "patch"
```

---

## EditorConfig

### `.editorconfig`

One universal file works for all repos — EditorConfig is language-aware. The canonical file is at `github/templates/editorconfig`.

### Rules

| Setting | Value | Rationale |
|---|---|---|
| Root | `true` | Stop searching for parent .editorconfig files |
| Charset | `utf-8` | Universal |
| End of line | `lf` | Unix line endings everywhere (even on Windows — git handles conversion) |
| Insert final newline | `true` | POSIX compliance |
| Trim trailing whitespace | `true` | Clean diffs |
| Indent style (Go) | `tabs` | `gofmt` requires tabs |
| Indent style (Java) | `spaces` (4) | Maven/Java convention |
| Indent style (TypeScript/JS) | `spaces` (2) | Prettier/ESLint convention |
| Indent style (Rust) | `tabs` | `rustfmt` default |
| Indent style (YAML/JSON/Markdown) | `spaces` (2) | Standard convention |
| Indent style (Makefile) | `tabs` | Make requires tabs |
| Indent style (Shell) | `spaces` (2) | Readable |

---

## Checklist for reviewing GitHub configuration

Before merging new or updated GitHub config, verify:

- [ ] `.github/ISSUE_TEMPLATE/bug_report.yml` exists with all 7 fields
- [ ] `.github/ISSUE_TEMPLATE/feature_request.yml` exists with all 3 fields
- [ ] `.github/PULL_REQUEST_TEMPLATE.md` exists with Description, Type of change, and Checklist sections
- [ ] `.github/dependabot.yml` exists with the correct ecosystems for the repo's languages
- [ ] `.editorconfig` exists at the repo root with `root = true`
- [ ] Dependabot schedule is weekly, grouped for minor/patch
- [ ] PR template checklist matches the repo's actual build commands
