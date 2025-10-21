"""Structured reporting for validation results."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Literal, Optional, Sequence


Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Issue:
    file: str
    line: int
    severity: Severity
    code: str
    message: str


@dataclass
class Report:
    issues: List[Issue] = field(default_factory=list)

    def add(self, issue: Issue) -> None:
        self.issues.append(issue)

    def extend(self, issues: Iterable[Issue]) -> None:
        self.issues.extend(list(issues))

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    def to_json(self) -> str:
        return json.dumps(
            [
                {
                    "file": i.file,
                    "line": i.line,
                    "severity": i.severity,
                    "code": i.code,
                    "message": i.message,
                }
                for i in self.issues
            ],
            ensure_ascii=False,
            indent=2,
        )

    def to_text(self, base_dir: Optional[str] = None) -> str:
        parts: List[str] = []
        for i in self.issues:
            file_display = i.file
            if base_dir and i.file.startswith(base_dir):
                try:
                    import os

                    file_display = os.path.relpath(i.file, base_dir)
                except Exception:
                    pass
            parts.append(f"{file_display}:{i.line}: {i.severity.upper()} {i.code} {i.message}")
        return "\n".join(parts)


