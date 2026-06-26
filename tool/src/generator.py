"""
generator.py — File generation from Jinja2 templates.

Single responsibility: render Jinja2 templates and write files to disk.
Knows nothing about validation or checking — only about creating files.
"""

import shutil
from pathlib import Path
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .archetypes import Archetype


class RepoGenerator:
    """Generates repository files from Jinja2 templates."""

    def __init__(self, guidelines_root: Path):
        """
        Args:
            guidelines_root: Path to the guidelines repo root
                             (for locating templates/ and static files).
        """
        self.guidelines_root = guidelines_root
        self.templates_dir = guidelines_root / "tool" / "templates"
        self.github_templates_dir = guidelines_root / "github" / "templates"
        self.markdownlint_dir = guidelines_root / "markdownlint"

        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            keep_trailing_newline=True,
            undefined=StrictUndefined,
        )

    def generate(
        self,
        archetype: Archetype,
        target: Path,
        context: Dict[str, str],
        dry_run: bool = False,
    ) -> Dict[str, bool]:
        """
        Generate all files for an archetype into the target directory.

        Args:
            archetype: The archetype definition (from archetypes.py)
            target: Target directory path
            context: Template variables (name, repo_name, language, etc.)
            dry_run: If True, don't write files — just report what would happen

        Returns:
            Dict mapping file path → True if created, False if skipped (existed)
        """
        results: Dict[str, bool] = {}

        # 1. Create directories
        for dir_path in archetype.directories:
            full = target / dir_path
            if not full.exists():
                if not dry_run:
                    full.mkdir(parents=True, exist_ok=True)
                results[f"dir:{dir_path}"] = True
            else:
                results[f"dir:{dir_path}"] = False

        # 2. Render Jinja2 templates
        for dest, template_name in archetype.file_templates.items():
            if template_name is None:
                continue
            created = self._render_template(
                template_name, target / dest, context, dry_run
            )
            results[dest] = created

        # 3. Copy static files
        for dest, source_name in archetype.copy_files.items():
            source_path = self._resolve_static_source(source_name)
            if source_path is None:
                results[dest] = False
                continue
            created = self._copy_file(source_path, target / dest, dry_run)
            results[dest] = created

        return results

    def _render_template(
        self,
        template_name: str,
        dest_path: Path,
        context: Dict[str, str],
        dry_run: bool,
    ) -> bool:
        """Render a Jinja2 template and write it. Returns True if written, False if existed."""
        if dest_path.exists():
            return False

        template = self.env.get_template(template_name)
        content = template.render(**context)

        if not dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(content, encoding="utf-8")
        return True

    def _copy_file(
        self,
        source: Path,
        dest: Path,
        dry_run: bool,
    ) -> bool:
        """Copy a file. Returns True if copied, False if existed."""
        if dest.exists():
            return False
        if not source.exists():
            return False
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        return True

    def _resolve_static_source(self, name: str) -> Optional[Path]:
        """Resolve a static file name to its source path in the guidelines repo."""
        # Try github/templates/ first (for editorconfig, bug_report.yml, etc.)
        candidate = self.github_templates_dir / name
        if candidate.exists():
            return candidate

        # Try markdownlint/ (for .markdownlint.json — file has dot prefix in that dir)
        candidate = self.markdownlint_dir / f".{name}"
        if candidate.exists():
            return candidate
        candidate = self.markdownlint_dir / name
        if candidate.exists():
            return candidate

        # Try guidelines root (for LICENSE)
        candidate = self.guidelines_root / name
        if candidate.exists():
            return candidate

        return None
