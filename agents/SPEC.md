# AGENTS.md Specification

This document defines the unified structure for `AGENTS.md` files across all quarkloop repositories. Every repository must have an `AGENTS.md` that follows this specification.

## Purpose

`AGENTS.md` is the operating manual for AI agents (Claude Code, Cursor, Aider, etc.) working on a repository. It is read before the agent touches any code. Its job is to prevent mistakes by giving the agent:

1. **What this repo is** — so the agent doesn't propose Rust changes to a Go repo
2. **What it must NOT do** — the redlines that will break things
3. **How to build and test** — the exact commands, not a wishy-washy "see CONTRIBUTING.md"
4. **Where things live** — so the agent doesn't create files in the wrong place
5. **How to commit** — message format, scope rules, what never to stage

## What AGENTS.md is NOT

- **Not CONTRIBUTING.md** — that is for humans. AGENTS.md is for machines.
- **Not ARCHITECTURE.md** — that describes the system. AGENTS.md describes how to work on it.
- **Not a README** — that is for users. AGENTS.md is for contributors (specifically AI contributors).
- **Not a design doc** — no philosophy, no "why we chose X over Y". Just rules and facts.

The tone should be **terse, imperative, and exhaustive about constraints**. No prose, no marketing, no "welcome contributors" warmth. AI agents read this file to avoid mistakes — give them the rules, not the philosophy.

## Line count targets

| Repo size | Target | Rationale |
|---|---|---|
| Small repos (1–5 source files, single language) | ≥ 200 lines | Enough room for all 8 sections with real content; not so long that the agent loses track |
| Large repos (multi-module, multi-language, 50+ source files) | ≥ 400 lines | Complex repos need more rules, more boundary descriptions, more module-specific guidance |

**Do not pad to hit the target.** If a small repo genuinely only needs 180 lines, that's fine — but look for places where you can add more specific rules, examples of what NOT to do, or per-module guidance. The goal is **better information and context for agents**, not line count for its own sake.

## The 8 sections

Every `AGENTS.md` must have these sections, in this exact order, with these exact headings:

---

### 1. `# Agent Guide`

The title, followed by a one-sentence statement of what this repo is and what an AI agent's job is here.

```markdown
# Agent Guide

This is the Quark JS SDK. Your job is to make focused, tested changes
that preserve the public API.
```

The statement should answer:
- What is this repo? (one clause)
- What is the agent's primary responsibility? (one clause)

---

### 2. `## Repository`

A compact metadata block. Always include these fields:

```markdown
## Repository

- **Name**: <human-readable name>
- **Language**: <primary language(s) and versions>
- **License**: <license name>
- **Repo**: <full GitHub URL>
- **Guidelines**: [quarkloop/guidelines](https://github.com/quarkloop/guidelines)
```

The **Guidelines** line is mandatory on every repo — it tells the agent where to find the full specification for AGENTS.md, README.md, and other org-wide conventions.

---

### 3. `## Quick reference`

The exact commands an agent needs. No prose, just a code block. This is the single most important section — an agent will run these commands dozens of times per session.

```markdown
## Quick reference

\`\`\`bash
make build          # build everything
make test           # run all tests
make check          # fmt + vet + test + arch-check (pre-commit gate)
make clean          # remove all build artifacts
\`\`\`
```

Rules:
- **Every command must have a one-line comment** explaining what it does.
- **No optional commands** — only the commands the agent will actually need.
- **No "see CONTRIBUTING.md"** — put the commands here, or don't have the section.
- If the repo has multiple languages with different test commands, list them all:

```markdown
\`\`\`bash
# Go
make test-go        # Go unit tests across all modules
make vet            # go vet across all modules

# Java
make test-java      # Maven unit tests
make build-native   # GraalVM native image (requires GraalVM 21+)

# Rust
cd services/harness && cargo test
\`\`\`
```

---

### 4. `## Structure`

Where things live. A tree with one-line annotations. An agent should be able to find any file type from this section alone.

```markdown
## Structure

\`\`\`
src/
├── index.ts          # public API barrel exports
├── types.ts          # all public interfaces and wire-protocol types
├── errors.ts         # QuarkError + subclasses
├── connection.ts     # transport layer (NATS connection, request-reply)
├── client.ts         # QuarkClient implementation
├── admin-client.ts   # QuarkAdminClient implementation
├── client-factory.ts # createClient()
├── admin-factory.ts  # createAdminClient()
├── node-handle.ts    # NodeHandle implementation
└── pipeline.ts       # PipelineBuilder implementation
\`\`\`
```

Rules:
- **Annotate every directory and key file** with a one-line description.
- **Use the `←` arrow** for annotations (consistent across all repos).
- **Show the real tree** — don't simplify or omit directories. The agent needs to know what exists.
- **For large repos**, show the top 2–3 levels. Don't go deeper than that in this section — use per-module descriptions in the Boundaries section instead.

---

### 5. `## Rules`

Imperative constraints. "Do X", "Do not Y". Numbered for easy reference. This is the section agents will be graded against — if an agent violates a rule listed here, that's a bug in the agent.

```markdown
## Rules

1. Do not break the public API without an explicit major version bump.
2. Do not add new top-level dependencies without discussing in an issue first.
3. Run `make check` before every commit — it must pass with zero errors.
4. Do not commit generated files (dist/, *.tsbuildinfo, .source/).
5. Do not disable TypeScript strict mode for individual files.
6. Do not use `require()` — this is an ESM-only package.
7. Do not export internal implementation classes (only export interfaces).
8. Every new function needs a unit test.
9. Every bug fix needs a regression test.
10. Inspect staged files before every commit.
```

Rules for writing rules:
- **Be specific.** "Do not pass ingress DTOs into domain packages" is good. "Follow best practices" is bad.
- **Be enforceable.** If you can't tell whether a rule was violated, it's not a rule — it's a guideline, and it belongs in CONTRIBUTING.md.
- **Be exhaustive.** Every constraint you wish an agent respected belongs here. 20 rules is fine. 50 rules is fine. 5 rules is too few.
- **Use positive and negative forms.** "Do X" and "Do not Y" are both valid. Mix them as needed.
- **Number them.** Makes it easy to reference specific rules in PR reviews.

For large repos, subdivide by concern:

```markdown
## Rules

### API stability
1. Do not break the public API without a major version bump.
2. Do not change error codes (they are part of the wire protocol).

### Dependencies
3. Do not add new top-level dependencies without an issue.
4. Do not bump dependency major versions without testing E2E.

### Code style
5. Run `make fmt` before every commit.
6. Do not disable linters for individual files.
...
```

---

### 6. `## Boundaries`

**Only for repos with multiple components/modules.** Small single-module repos can skip this section.

What each module owns and what it must not depend on. Prevents an agent from creating cross-module coupling.

```markdown
## Boundaries

- `supervisor` owns high-level space/session orchestration, plugin installs,
  embedded NATS, account setup, runtime leases, and discovery catalogs.
- `runtime` owns the agent loop, sessions, tool execution, workspace sidecar
  policy, and consumption of supervisor-resolved catalogs.
- `cli` is a NATS client. It selects a space through `--space` or
  `QUARK_SPACE` and delegates state operations to supervisor or runtime.
- `services/*` own durable domain behavior behind protobuf-backed NATS
  service-function contracts. Services must not call each other.
- `pkg/serviceapi` owns protobuf contracts and NATS service-function helpers.
```

Rules:
- **One bullet per module.** Describe what it owns, not how it works.
- **Call out what it must NOT depend on.** "Services must not call each other" is more important than what they do.
- **Use the module's directory name** (not a friendly name) so the agent can grep for it.

For very large repos, add a dependency graph:

```markdown
\`\`\`
main.rs
  ↓
bridge.rs ───► catalog.rs ──► native.rs
  │                              ↑
  ├──► native.rs ────────────────┘
  │
  ├──► wasm.rs ──► wasm_cache.rs
  │
  └──► shutdown.rs
\`\`\`

No cycles. `native.rs` and `wasm.rs` are siblings — neither knows
about the other.
```

---

### 7. `## Commit conventions`

How to write commits. AI agents commit frequently — this section prevents noisy history.

```markdown
## Commit conventions

- Format: `type(scope): short summary`
- Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `build`
- One scope per commit — do not mix unrelated changes.
- Inspect staged files before every commit: `git diff --cached --stat`
- Never stage: `.env`, `node_modules/`, `dist/`, `*.tsbuildinfo`, editor configs.
- Do not include `Co-authored-by` trailers.
- Do not use destructive git commands unless explicitly requested.
- Conventional commit examples:
  - `feat(client): add streaming support for batch calls`
  - `fix(pipeline): preserve step output when partialInput is null`
  - `docs(readme): add web UI setup instructions`
```

Rules:
- **List the exact types** the repo uses (some repos may not use all Conventional Commits types).
- **List what never to stage** — this is repo-specific and prevents real mistakes.
- **Show examples** — agents learn better from examples than from rules.

---

### 8. `## Testing`

What to test, how to test it, what counts as "done".

```markdown
## Testing

- Every new function needs a unit test in the same package.
- Every bug fix needs a regression test that would have caught the bug.
- Run `make test` — must pass with zero failures before committing.
- For E2E: `make test-e2e` (requires NATS server running on localhost:4222).
- Tests must not pre-extract or pre-index data that the agent is supposed
  to process — let the agent do the work.
- Test files use the `_test.go` suffix (Go) or `.test.ts` suffix (TypeScript).
```

Rules:
- **State the test file naming convention** so the agent knows where to put tests.
- **State what "done" means** — "must pass with zero failures" is unambiguous.
- **Call out E2E requirements** — external services, API keys, Docker, etc.
- **State anti-patterns** — things agents commonly do wrong in tests (pre-extracting data, mocking too much, testing implementation instead of behavior).

---

## Reference line (mandatory)

Every `AGENTS.md` must include this line in the **Repository** section:

```markdown
- **Guidelines**: [quarkloop/guidelines](https://github.com/quarkloop/guidelines)
```

This tells the agent where to find the full specification for AGENTS.md, README.md, and other org-wide conventions. If the agent is working across multiple quarkloop repos, it can read the guidelines repo once and apply the conventions everywhere.

---

## What does NOT belong in AGENTS.md

| Content | Belongs in | Why |
|---|---|---|
| Architecture deep-dive (component diagrams, data flow, design decisions) | `docs/architecture.mdx` | Too long; agents read it on-demand |
| API reference (every method, every type, every error code) | `docs/api.mdx` | Reference material, not rules |
| Build prerequisites (install Go, install Node, etc.) | `docs/build.mdx` | One-time setup, not per-task |
| Contributing workflow (PR process, code review, forking) | `CONTRIBUTING.md` | For humans, not agents |
| Security policy | `SECURITY.md` | Standard convention — GitHub auto-detects |
| Code of Conduct | `CODE_OF_CONDUCT.md` | Standard convention — GitHub auto-detects |
| Changelog | `CHANGELOG.md` | Standard convention — GitHub auto-detects |
| Marketing copy / project description | `README.md` | AGENTS.md is for agents, not users |

---

## Good vs bad examples

### Good rules (specific, enforceable)

```
1. Do not pass ingress DTOs into domain packages.
2. Run `make check` before every commit.
3. Never stage `docs/` changes — those are local task tracking only.
4. Do not make services call each other.
5. Do not reintroduce a runtime "capability" abstraction.
```

### Bad rules (vague, unenforceable)

```
1. Follow best practices.
2. Keep code clean.
3. Write good tests.
4. Be consistent with existing code.
5. Don't break things.
```

The difference: a good rule can be checked by running a command or reading a diff. A bad rule requires judgment that an AI agent may not have.

---

## Per-repo adaptation guide

### Small repos (≥ 200 lines)

- All 8 sections are present.
- The **Rules** section has 10–20 rules.
- The **Boundaries** section may be short (one module) or omitted.
- The **Structure** section shows the full file tree.
- No subdivision within sections.

### Large repos (≥ 400 lines)

- All 8 sections are present.
- The **Rules** section has 20–50 rules, subdivided by concern (API stability, dependencies, code style, testing, etc.).
- The **Boundaries** section is detailed — one bullet per module, plus a dependency graph.
- The **Structure** section shows top 2–3 levels; deeper structure is described in per-module paragraphs.
- The **Quick reference** section has multiple code blocks (one per language or component).
- The **Testing** section describes unit, integration, and E2E separately.

### Multi-language repos

- The **Quick reference** section has separate code blocks for each language.
- The **Rules** section has language-specific subsections.
- The **Boundaries** section calls out which language owns which module.

---

## Checklist for reviewing an AGENTS.md

Before merging a new or updated AGENTS.md, verify:

- [ ] All 8 sections are present, in the correct order.
- [ ] The **Repository** section includes the **Guidelines** line pointing to `quarkloop/guidelines`.
- [ ] The **Quick reference** section has exact commands with comments — no "see CONTRIBUTING.md".
- [ ] The **Structure** section shows the real file tree with annotations.
- [ ] The **Rules** section has specific, enforceable rules — no "follow best practices".
- [ ] The **Boundaries** section (if present) lists what each module owns and must not depend on.
- [ ] The **Commit conventions** section lists what never to stage.
- [ ] The **Testing** section states what "done" means.
- [ ] Line count meets the target (≥ 200 for small, ≥ 400 for large).
- [ ] No architecture deep-dives, API references, or build prerequisites (those belong in `docs/`).
- [ ] No marketing copy or human-oriented warmth (this is for machines).
