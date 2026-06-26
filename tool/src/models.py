"""
models.py — Data models for validation results.

Single responsibility: define the data structures used by checks and
validators. No logic, no I/O.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CheckResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    message: str = ""
    detail: str = ""
    suggestion: str = ""  # actionable fix suggestion (for doctor mode)


@dataclass
class ValidationReport:
    """Collection of check results for one repository."""
    repo_path: str
    results: List[CheckResult] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def all_passed(self) -> bool:
        return self.failed_count == 0

    def add(self, name: str, passed: bool, message: str = "",
            detail: str = "", suggestion: str = ""):
        """Append a check result."""
        self.results.append(
            CheckResult(name, passed, message, detail, suggestion)
        )

    @property
    def failed_results(self) -> List[CheckResult]:
        """Return only the failed checks."""
        return [r for r in self.results if not r.passed]
