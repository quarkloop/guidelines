# README.md Specification

This document defines the unified structure for `README.md` files across all quarkloop repositories. Every repository must have a `README.md` that follows this specification.

## Purpose

`README.md` is the entry point for a repository. It is read by:

- **Users** deciding whether to use the project
- **Developers** setting up a local environment
- **AI agents** getting a high-level overview before reading `AGENTS.md`

It should answer three questions in under 2 minutes of reading:

1. **What is this?** (Overview)
2. **How do I install it?** (Installation)
3. **How do I get it running?** (Quick start)

Everything else belongs in linked documentation files.

## Line count target

**Under 200 lines.** If the README is longer, content is being duplicated from `docs/` files. The README is an overview and entry point, not a reference manual.

## The 8 sections

Every `README.md` must have these sections, in this exact order, with these exact headings:

---

### 1. `# <Project Name>`

The title, followed by an optional one-sentence tagline. Use the **product name**, not the package name.

```markdown
# Quark JS SDK

TypeScript SDK for [Quark](https://github.com/quarkloop/quark) — execute nodes by URI, chain them in pipelines, browse the catalog.
```

Optional: badges (CI status, language version, license) on the line below the title. Maximum 3 badges — more is noise.

```markdown
[![CI](https://github.com/quarkloop/agent/actions/workflows/ci.yml/badge.svg)](https://github.com/quarkloop/agent/actions/workflows/ci.yml)
[![Go 1.26+](https://img.shields.io/badge/go-1.26+-00ADD8.svg)](https://go.dev/dl/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
```

Rules:
- **Use the product name** ("Quark JS SDK"), not the package name ("@quarkloop/quark-js").
- **One-sentence tagline** describes what it does, not how it's built.
- **Badges are optional** — only include if CI is set up and passing.

---

### 2. `## Overview`

2–3 sentences. What this is, who it's for, what problem it solves. No technical implementation details here — just the value proposition.

```markdown
## Overview

The Quark JS SDK is the primary way for TypeScript applications to talk to a
Quark deployment. Quark hosts small functions ("nodes") written in Rust, Go,
Java, or any language that compiles to a shared library or WebAssembly. This
SDK lets your application call them over the network.
```

Rules:
- **2–3 sentences.** Not a paragraph, not a page.
- **No implementation details.** Don't mention NATS, GraalJS, SQLite, or other internals unless the user needs to know about them to use the product.
- **No marketing fluff.** "The fastest, most elegant, most powerful..." — delete all of that.
- **Who it's for.** Make clear whether this is for application developers, operators, or contributors.

---

### 3. `## Features`

Bullet list of 4–8 key capabilities. Scannable in 5 seconds. One line each, no nested bullets.

```markdown
## Features

- **Node execution** — run any node by URI with a single `await quark.run(uri, input)` call
- **Pipelines** — chain node calls where each step's output feeds the next step's input
- **Batch execution** — run multiple nodes in parallel with `Promise.all` semantics
- **Catalog browsing** — list, search, and inspect nodes registered with the runtime
- **Admin operations** — health checks, runtime status, and (planned) push/delete/pull/flushCache
- **Typed errors** — every error extends `QuarkError` with a `code` field for programmatic handling
```

Rules:
- **4–8 bullets.** Fewer is too sparse; more is overwhelming.
- **Bold the feature name** followed by an em-dash and a one-line description.
- **No nested bullets.** If a feature needs sub-points, it belongs in `docs/`.
- **Scannable in 5 seconds.** A reader should get the gist without reading the descriptions.

---

### 4. `## Installation`

Per-runtime tabs or sections. Just the commands, no commentary. Cover every runtime the project supports.

```markdown
## Installation

### npm

\`\`\`bash
npm install @quarkloop/quark-js
\`\`\`

### Bun

\`\`\`bash
bun add @quarkloop/quark-js
\`\`\`

### Deno

Add to your `deno.json` imports:

\`\`\`json
{
  "imports": {
    "@quarkloop/quark-js": "npm:@quarkloop/quark-js@^0.1.0"
  }
}
\`\`\`
```

For non-package repos (platforms, runtimes):

```markdown
## Installation

\`\`\`bash
git clone https://github.com/quarkloop/quark.git
cd quark
make build
\`\`\`

See [Build & development](./docs/build.mdx) for full prerequisites.
```

Rules:
- **Every supported runtime gets its own subsection.**
- **Just the commands.** No "first, make sure you have Node.js installed" — that's in `docs/build.mdx`.
- **Link to build docs** for repos with complex prerequisites.

---

### 5. `## Quick start`

One minimal end-to-end example. ~10–20 lines of code or shell. The reader should be able to copy-paste and get a "hello world" working in under 2 minutes.

```markdown
## Quick start

\`\`\`typescript
import { createClient, createAdminClient } from '@quarkloop/quark-js';

const quark = await createClient({
  servers: ['localhost:4222'],
});

// Execute a node by URI:
const result = await quark.run('myorg/myteam/validate:v1', {
  servers: [{ host: 'web-01', port: 443, protocol: 'https' }],
});

await quark.close();
\`\`\`
```

Rules:
- **One example.** Not three, not five. One.
- **Minimal.** No error handling, no edge cases, no advanced options. Just the happy path.
- **Copy-pasteable.** The reader should be able to run it without modification (after installing).
- **No commentary between code lines.** Comments inside the code block are fine; prose between code blocks is not.

For non-package repos:

```markdown
## Quick start

\`\`\`bash
# 1. Start NATS:
nats-server &

# 2. Build everything:
make build

# 3. Run the example:
make run-example
\`\`\`
```

---

### 6. `## Documentation`

Link list to detailed docs. Each link is a separate `.mdx` file in the repo's `docs/` directory (or root-level for repos without a `docs/` directory).

```markdown
## Documentation

- [Architecture](./docs/architecture.mdx) — source layout, transport layer, design rationale
- [API reference](./docs/api.mdx) — every public type, function, and error class
- [Build & development](./docs/build.mdx) — local setup, type-checking, testing
- [Changelog](./CHANGELOG.md) — release history
- [Contributing](./CONTRIBUTING.md) — development setup, PR workflow, code style
```

Rules:
- **One bullet per doc file.** Don't group or nest.
- **Format: `[Title](path) — one-line description`.**
- **List the most important docs first** (Architecture, API, Build). Standard files (Changelog, Contributing, Security) go last.
- **Only link docs that exist.** Don't link to planned docs.

---

### 7. `## Compatibility`

Table or short list of supported runtimes / OSes / versions.

```markdown
## Compatibility

| Component | Language | Version |
|---|---|---|
| Bun | — | ≥ 1.0 |
| Node.js | — | ≥ 20 (with a TypeScript loader) |
| Deno | — | ≥ 1.30 |
```

Or for multi-component repos:

```markdown
## Compatibility

| Component | Language | Version |
|---|---|---|
| Control plane (`quark-server/`) | Go | 1.24+ |
| Catalog service (`quark-catalog/`) | Go | 1.24+ |
| Data plane (`quark-runtime/`) | Java | JDK 21+ (GraalVM 21+ for native mode) |
| NATS server | — | 2.10+ |
```

Rules:
- **Use a table** if there are 3+ components. Use a list if there are 1–2.
- **Include version numbers** — "latest" is not a version.
- **Call out optional prerequisites** (e.g., "GraalVM 21+ for native mode").

---

### 8. `## Contributing`

One paragraph + link to `CONTRIBUTING.md`. Mention that contributors agree to the Code of Conduct.

```markdown
## Contributing

Pull requests are welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for
development setup, commit message conventions, and code style rules. By
participating you agree to abide by the
[Code of Conduct](./CODE_OF_CONDUCT.md).
```

Rules:
- **One paragraph.** Don't duplicate the CONTRIBUTING.md content here.
- **Link both CONTRIBUTING.md and CODE_OF_CONDUCT.md.**
- **No "issues and PRs are welcome" warmth** — that's implied.

---

### 9. `## License`

One line. Standard wording.

```markdown
## License

This project is licensed under the Apache License, Version 2.0 — see the
[LICENSE](./LICENSE) file for details.
```

Or for MIT:

```markdown
## License

This project is licensed under the MIT License — see the
[LICENSE](./LICENSE) file for details.
```

Rules:
- **Use the exact wording** above for consistency across repos.
- **Always link to the LICENSE file** — don't inline the license text.

---

## What moves OUT of README

These belong in dedicated files, linked from the Documentation section:

| Content type | File | Why it doesn't belong in README |
|---|---|---|
| Architecture deep-dive (component diagrams, data flow, design decisions) | `docs/architecture.mdx` | Too long; only useful once you're already using the project |
| Full API reference (every method, every type, every error code) | `docs/api.mdx` | Reference material, not introduction |
| Wire protocol specs (NATS subjects, request/response shapes) | `docs/protocol.mdx` | Implementation detail; only useful for integrators |
| Build system details (Makefile targets, Docker, native-image) | `docs/build.mdx` | Most users don't need this |
| Examples | `examples/` directory with own READMEs | Discoverable by browsing, not by scrolling README |
| Security policy | `SECURITY.md` | Standard convention — GitHub auto-detects |
| Code of conduct | `CODE_OF_CONDUCT.md` | Standard convention — GitHub auto-detects |
| Contributing guide | `CONTRIBUTING.md` | Standard convention — GitHub auto-detects |
| Changelog | `CHANGELOG.md` | Standard convention — GitHub auto-detects |
| AI agent guide | `AGENTS.md` | For AI agents, not human users |

---

## Checklist for reviewing a README

Before merging a new or updated README, verify:

- [ ] All 9 sections are present, in the correct order.
- [ ] Title uses the product name, not the package name.
- [ ] Overview is 2–3 sentences with no implementation details.
- [ ] Features has 4–8 bullets, each one line.
- [ ] Installation covers every supported runtime.
- [ ] Quick start is one minimal, copy-pasteable example.
- [ ] Documentation links to existing `.mdx` files in `docs/`.
- [ ] Compatibility has version numbers, not "latest".
- [ ] Contributing is one paragraph linking CONTRIBUTING.md and CODE_OF_CONDUCT.md.
- [ ] License uses the standard wording and links to LICENSE.
- [ ] Total length is under 200 lines.
- [ ] No architecture deep-dives, API references, or build prerequisites (those belong in `docs/`).
- [ ] No marketing copy or superlatives.
