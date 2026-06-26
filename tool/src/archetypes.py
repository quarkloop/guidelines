"""
archetypes.py — Repository archetype definitions.

Single responsibility: define what directories and files each archetype
needs, and which template to use for each generated file. Pure data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Archetype:
    """Definition of a repository archetype."""
    name: str
    description: str
    directories: List[str]
    # Map of destination path → template name (None means copy from guidelines)
    # Template names are relative to tool/templates/
    # None means copy the file from the guidelines repo root
    file_templates: Dict[str, Optional[str]] = field(default_factory=dict)
    # Files that are copied verbatim from github/templates/
    copy_files: Dict[str, str] = field(default_factory=dict)


LIBRARY = Archetype(
    name="library",
    description="Single-language library (TypeScript, Go, Rust, or Java)",
    directories=["src", "docs", "examples", ".github/ISSUE_TEMPLATE"],
    file_templates={
        "AGENTS.md": "agents.md.j2",
        "README.md": "readme.md.j2",
        "CONTRIBUTING.md": "contributing.md.j2",
        "SECURITY.md": "security.md.j2",
        "CHANGELOG.md": "changelog.md.j2",
        "CODE_OF_CONDUCT.md": "code_of_conduct.md.j2",
        ".github/PULL_REQUEST_TEMPLATE.md": "pr_template.md.j2",
        ".github/dependabot.yml": "dependabot.yml.j2",
        ".gitignore": "gitignore.j2",
        ".markdownlintignore": "markdownlintignore.j2",
    },
    copy_files={
        ".github/ISSUE_TEMPLATE/bug_report.yml": "bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml": "feature_request.yml",
        ".editorconfig": "editorconfig",
        ".markdownlint.json": "markdownlint.json",
        "LICENSE": "LICENSE",
    },
)

PLATFORM = Archetype(
    name="platform",
    description="Multi-language platform (Go + Java + Rust, etc.)",
    directories=["docs", "deploy", "scripts", "proto", "e2e", ".github/ISSUE_TEMPLATE"],
    file_templates={
        "AGENTS.md": "agents.md.j2",
        "README.md": "readme.md.j2",
        "CONTRIBUTING.md": "contributing.md.j2",
        "SECURITY.md": "security.md.j2",
        "CHANGELOG.md": "changelog.md.j2",
        "CODE_OF_CONDUCT.md": "code_of_conduct.md.j2",
        ".github/PULL_REQUEST_TEMPLATE.md": "pr_template.md.j2",
        ".github/dependabot.yml": "dependabot.yml.j2",
        ".gitignore": "gitignore.j2",
        ".markdownlintignore": "markdownlintignore.j2",
    },
    copy_files={
        ".github/ISSUE_TEMPLATE/bug_report.yml": "bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml": "feature_request.yml",
        ".editorconfig": "editorconfig",
        ".markdownlint.json": "markdownlint.json",
        "LICENSE": "LICENSE",
    },
)

DOCS = Archetype(
    name="docs",
    description="Documentation site (Next.js / Fuma Docs)",
    directories=["app", "components", "lib", "scripts", "content", "public", ".github/ISSUE_TEMPLATE"],
    file_templates={
        "AGENTS.md": "agents.md.j2",
        "README.md": "readme.md.j2",
        ".github/PULL_REQUEST_TEMPLATE.md": "pr_template.md.j2",
        ".github/dependabot.yml": "dependabot.yml.j2",
        ".gitignore": "gitignore.j2",
        ".markdownlintignore": "markdownlintignore.j2",
    },
    copy_files={
        ".github/ISSUE_TEMPLATE/bug_report.yml": "bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml": "feature_request.yml",
        ".editorconfig": "editorconfig",
        ".markdownlint.json": "markdownlint.json",
        "LICENSE": "LICENSE",
    },
)

SPECS = Archetype(
    name="specs",
    description="Specifications repository (like guidelines)",
    directories=[".github/ISSUE_TEMPLATE"],
    file_templates={
        "AGENTS.md": "agents.md.j2",
        "README.md": "readme.md.j2",
        ".github/PULL_REQUEST_TEMPLATE.md": "pr_template.md.j2",
        ".github/dependabot.yml": "dependabot.yml.j2",
        ".gitignore": "gitignore.j2",
    },
    copy_files={
        ".github/ISSUE_TEMPLATE/bug_report.yml": "bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml": "feature_request.yml",
        ".editorconfig": "editorconfig",
        ".markdownlint.json": "markdownlint.json",
        "LICENSE": "LICENSE",
    },
)

ARCHETYPES: Dict[str, Archetype] = {
    "library": LIBRARY,
    "platform": PLATFORM,
    "docs": DOCS,
    "specs": SPECS,
}


def get_archetype(name: str) -> Archetype:
    """Look up an archetype by name. Raises KeyError if not found."""
    return ARCHETYPES[name]
