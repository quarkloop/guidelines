# Markdown Linting Specification

This document defines the unified markdown linting rules for all quarkloop repositories.

## Purpose

Consistent markdown formatting across all repos:

- Prevents formatting drift (mixed heading styles, inconsistent list markers, trailing whitespace)
- Makes diffs cleaner — only content changes, not formatting
- Catches common mistakes (bare HTML that breaks rendering, duplicate headings, broken links)

## Required files

Every repository must have:

| File | Purpose |
|---|---|
| `.markdownlint.json` | Markdownlint CLI2 configuration (rule overrides) |
| `.markdownlintignore` | Files to exclude from linting (optional, repo-specific) |

## Configuration

The canonical configuration is at `markdownlint/.markdownlint.json`. It enables most rules with these overrides:

### Disabled rules (with rationale)

| Rule | Why disabled |
|---|---|
| `MD013` (line-length) | Markdown wraps naturally in editors; enforcing 80 chars breaks tables and links |
| `MD033` (no-inline-html) | MDX files use HTML/JSX components (Callout, Tabs, Steps); plain `.md` files may use `<details>`/`<summary>` |
| `MD041` (first-line-heading) | Some files start with frontmatter (`---`), which is not a heading |
| `MD024` (no-duplicate-heading) | Common pattern: multiple `## Example` or `## Parameters` sections in different contexts |

### Enabled rules (notable)

| Rule | What it enforces |
|---|---|
| `MD001` | Heading increment by one level at a time (`#` → `##` → `###`, never `#` → `###`) |
| `MD009` | No trailing whitespace (except in `.md`/`.mdx` where two trailing spaces = line break) |
| `MD010` | No hard tabs in markdown (tabs in code blocks are fine) |
| `MD012` | No multiple consecutive blank lines |
| `MD025` | Only one top-level `#` heading per file |
| `MD031` | Fenced code blocks must be surrounded by blank lines |
| `MD032` | Lists must be surrounded by blank lines |
| `MD040` | Fenced code blocks must specify a language |
| `MD047` | File must end with a single newline |

### MDX-specific handling

MDX files (`.mdx`) are linted with the same rules as `.md` files, with one exception: inline HTML/JSX is allowed (MD033 disabled). This is because MDX uses components like `<Callout>`, `<Tabs>`, and `<Steps>`.

## Ignoring files

### Standard ignores (all repos)

```
node_modules/
.next/
.vercel/
dist/
target/
bin/
.source/
content/          # docs repo — synced content, not authored here
public/pagefind/  # docs repo — generated
```

### Repo-specific ignores

Each repo may add a `.markdownlintignore` for files that shouldn't be linted:

| Repo | Ignored paths | Reason |
|---|---|---|
| `agent` | `e2e/testdata/*` | Test fixtures (PDFs, generated markdown) |
| `agent` | `proto/*/gen/*` | Generated protobuf stubs |
| `quark` | `docs/content/*` | Legacy content dir (if any remains) |
| `guidelines` | (none) | All markdown is authored |

## Running markdownlint

### Local

```bash
# Install markdownlint-cli2 globally (one-time)
npm install -g markdownlint-cli2

# Lint all markdown in the repo
markdownlint-cli2 '**/*.md' '**/*.mdx'

# Lint a specific file
markdownlint-cli2 'README.md'
```

### VS Code

Install the `markdownlint` extension (DavidAnson.vscode-markdownlint). It reads `.markdownlint.json` automatically.

### CI (planned)

Add a markdownlint step to the CI workflow:

```yaml
- name: Markdown lint
  run: npx markdownlint-cli2 '**/*.md' '**/*.mdx'
```

## Checklist for reviewing markdown linting config

- [ ] `.markdownlint.json` exists at repo root
- [ ] `.markdownlintignore` exists if the repo has generated/test markdown
- [ ] `markdownlint-cli2 '**/*.md' '**/*.mdx'` passes with zero errors
- [ ] No rules disabled beyond the 4 standard overrides (MD013, MD033, MD041, MD024)
