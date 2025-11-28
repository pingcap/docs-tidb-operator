"""Image reference validation for Markdown files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .fs_utils import ensure_within, read_text_file
from .markdown_parser import extract_images
from .report import Issue


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


@dataclass(frozen=True)
class ImageIssue(Issue):
    pass


def _normalize_image_path(base_file: str, src: str, repo_root: str) -> Optional[str]:
    if src.startswith("/"):
        candidate = os.path.join(repo_root, src.lstrip("/"))
    else:
        candidate = os.path.join(os.path.dirname(base_file), src)
    candidate = os.path.normpath(candidate)
    return ensure_within(candidate, repo_root)


def check_markdown_images(file_path: str, repo_root: str) -> List[ImageIssue]:
    issues: List[ImageIssue] = []
    content = read_text_file(file_path)
    images = extract_images(content)

    for img in images:
        src = img.src
        name, ext = os.path.splitext(src)

        normalized = _normalize_image_path(file_path, src, repo_root)
        if not normalized:
            issues.append(
                ImageIssue(
                    file=file_path,
                    line=img.line,
                    severity="error",
                    code="PATH_TRAVERSAL",
                    message=f"Image path escapes repository root: {src}",
                )
            )
            continue

        if not os.path.exists(normalized):
            issues.append(
                ImageIssue(
                    file=file_path,
                    line=img.line,
                    severity="error",
                    code="MISSING_IMAGE",
                    message=f"Image file not found: {src}",
                )
            )
            continue

        # Warn for uncommon image extensions
        if ext.lower() not in IMAGE_EXTENSIONS:
            issues.append(
                ImageIssue(
                    file=file_path,
                    line=img.line,
                    severity="warning",
                    code="UNCOMMON_EXT",
                    message=f"Uncommon image extension '{ext}' for {src}",
                )
            )

    return issues


