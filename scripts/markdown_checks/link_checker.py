"""Link and anchor validation for Markdown files.

Checks performed:
- External HTTP(S) links: syntax validated; optional network checks are disabled by default
- Local relative links: verify target file exists within repo
- Anchor fragments (e.g., file.md#section): verify heading slug exists in target file
- Intra-file anchors (#section): verify against the same file
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Tuple

from .fs_utils import read_text_file, ensure_within
from .markdown_parser import extract_headings, extract_links
from .report import Issue


@dataclass(frozen=True)
class LinkIssue(Issue):
    pass


def _split_url(url: str) -> Tuple[str, Optional[str]]:
    if "#" in url:
        base, frag = url.split("#", 1)
        return base, frag
    return url, None


def _is_external(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def _normalize_path(base_file: str, url_path: str, repo_root: str) -> Optional[str]:
    # Handle absolute paths rooted at repo root like /media/foo.png -> repo_root/media/foo.png
    if url_path.startswith("/"):
        candidate = os.path.join(repo_root, url_path.lstrip("/"))
    else:
        candidate = os.path.join(os.path.dirname(base_file), url_path)
    candidate = os.path.normpath(candidate)
    return ensure_within(candidate, repo_root)


def _collect_headings(file_path: str) -> List[str]:
    content = read_text_file(file_path)
    return [h.slug for h in extract_headings(content)]


def check_markdown_links(file_path: str, repo_root: str) -> List[LinkIssue]:
    """Validate links in a single Markdown file.

    Args:
        file_path: Absolute path to the markdown file.
        repo_root: Absolute path to the repository root.
    """

    issues: List[LinkIssue] = []
    content = read_text_file(file_path)
    links = extract_links(content)

    # Pre-compute current file headings for intra-file anchors
    current_headings = set(_collect_headings(file_path))

    for link in links:
        url = link.url
        base, frag = _split_url(url)

        if _is_external(base):
            # External link: we don't fetch network, but basic sanity check
            if " " in base:
                issues.append(
                    LinkIssue(
                        file=file_path,
                        line=link.line,
                        severity="warning",
                        code="LINK_WHITESPACE",
                        message=f"External link contains spaces: {base}",
                    )
                )
            continue

        # Handle mailto: and other schemes
        if ":" in base and not base.startswith("./") and not base.startswith("../") and not base.startswith("/"):
            # Non-file scheme; skip
            continue

        if base == "":
            # Pure fragment link like #section
            if not frag:
                issues.append(
                    LinkIssue(
                        file=file_path,
                        line=link.line,
                        severity="warning",
                        code="EMPTY_LINK",
                        message="Empty link target",
                    )
                )
                continue
            if frag not in current_headings:
                issues.append(
                    LinkIssue(
                        file=file_path,
                        line=link.line,
                        severity="error",
                        code="MISSING_ANCHOR",
                        message=f"Anchor not found in file: #{frag}",
                    )
                )
            continue

        normalized = _normalize_path(file_path, base, repo_root)
        if not normalized:
            issues.append(
                LinkIssue(
                    file=file_path,
                    line=link.line,
                    severity="error",
                    code="PATH_TRAVERSAL",
                    message=f"Link escapes repository root: {base}",
                )
            )
            continue

        if not os.path.exists(normalized):
            issues.append(
                LinkIssue(
                    file=file_path,
                    line=link.line,
                    severity="error",
                    code="MISSING_FILE",
                    message=f"Linked file not found: {base}",
                )
            )
            continue

        if frag:
            headings = set(_collect_headings(normalized))
            if frag not in headings:
                issues.append(
                    LinkIssue(
                        file=file_path,
                        line=link.line,
                        severity="error",
                        code="MISSING_ANCHOR",
                        message=f"Anchor not found in target: {base}#{frag}",
                    )
                )

    return issues


