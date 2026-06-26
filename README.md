# Quarkloop Guidelines

Unified specifications for `AGENTS.md` and `README.md` files across all quarkloop repositories. This repo defines the templates, section rules, and review checklists that every quarkloop repo must follow.

## Overview

Consistency across repositories reduces cognitive load for contributors and gives AI agents a predictable structure to work within. This repo contains the canonical specifications — each product repo's `AGENTS.md` and `README.md` is an instance of the templates defined here.

## Specifications

- [AGENTS.md Specification](./agents/SPEC.md) — the 8-section template for AI agent guides (line targets, section rules, good vs bad examples, review checklist)
- [README.md Specification](./readme/SPEC.md) — the 9-section template for repository READMEs (what goes in each section, what moves to `docs/`, review checklist)

## How to use

### When creating a new repo

1. Read both specs in full.
2. Create `AGENTS.md` following the 8-section template. Include the **Guidelines** line in the Repository section pointing to this repo.
3. Create `README.md` following the 9-section template.
4. Run through the review checklist for each file before merging.

### When updating an existing repo

1. Read the relevant spec.
2. Compare your current `AGENTS.md` / `README.md` against the template.
3. Fill in missing sections, trim content that belongs in `docs/`, and verify line counts meet the targets.
4. Run through the review checklist before merging.

### When updating the specifications

1. Edit the spec file in this repo.
2. Open a PR describing what changed and why.
3. Once merged, each product repo should update its `AGENTS.md` / `README.md` to match at its own pace — no coordinated migration needed.

## Line count targets

| File | Small repos | Large repos |
|---|---|---|
| `AGENTS.md` | ≥ 200 lines | ≥ 400 lines |
| `README.md` | < 200 lines | < 200 lines |

**Rationale:** AGENTS.md should give agents better information and context — more is better as long as it's specific and enforceable. README should be an overview and entry point — shorter is better; detailed reference belongs in `docs/`.

## Structure

```
guidelines/
├── README.md              ← this file
├── LICENSE                ← Apache 2.0
├── agents/
│   └── SPEC.md            ← AGENTS.md specification (8 sections)
└── readme/
    └── SPEC.md            ← README.md specification (9 sections)
```

## Contributing

Pull requests are welcome. If you want to add a new specification (e.g., `CONTRIBUTING.md` spec, `CHANGELOG.md` spec), create a new directory with a `SPEC.md` file and update this README.

By participating you agree to abide by the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct.

## License

This project is licensed under the Apache License, Version 2.0 — see the [LICENSE](./LICENSE) file for details.
