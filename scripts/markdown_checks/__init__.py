"""Markdown validation toolkit for TiDB Operator docs.

This package provides utilities and checkers to validate Markdown content:

- File system utilities to walk trees and read files safely
- Markdown parser to extract links, images, and headings
- Link checker for internal paths and anchors
- Image checker to verify referenced images exist and are used
- Reporting utilities for human and machine-readable output

Usage is typically via the CLI wrapper in `scripts/validate_docs.py`.
"""

from .fs_utils import (
    find_files,
    read_text_file,
    is_relative_to,
)
from .markdown_parser import (
    extract_links,
    extract_images,
    extract_headings,
)
from .link_checker import (
    check_markdown_links,
    LinkIssue,
)
from .image_checker import (
    check_markdown_images,
    ImageIssue,
)
from .report import (
    Report,
    Issue,
)

__all__ = [
    "find_files",
    "read_text_file",
    "is_relative_to",
    "extract_links",
    "extract_images",
    "extract_headings",
    "check_markdown_links",
    "check_markdown_images",
    "LinkIssue",
    "ImageIssue",
    "Report",
    "Issue",
]


