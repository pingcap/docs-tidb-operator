"""File system utilities for the Markdown validation toolkit.

These helpers are intentionally small and dependency-free to ensure that
validation can run in constrained CI environments.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Tuple


DEFAULT_MARKDOWN_GLOBS: Tuple[str, ...] = (".md",)


@dataclass(frozen=True)
class FileDiscoveryConfig:
    """Configuration for file discovery.

    Attributes:
        root: Directory where discovery begins.
        include_extensions: File extensions to include (e.g., ".md").
        exclude_dirs: Directory names to skip entirely.
        follow_symlinks: Whether to traverse symlinked directories.
    """

    root: str
    include_extensions: Tuple[str, ...] = DEFAULT_MARKDOWN_GLOBS
    exclude_dirs: Tuple[str, ...] = (
        ".git",
        ".github",
        "node_modules",
        "venv",
        ".venv",
        "_build",
        "build",
        "dist",
    )
    follow_symlinks: bool = False


def is_relative_to(path: str, root: str) -> bool:
    """Return True if path is inside root directory tree.

    Works across platforms and normalizes separators.
    """

    try:
        normalized_path = os.path.realpath(os.path.abspath(path))
        normalized_root = os.path.realpath(os.path.abspath(root))
        common = os.path.commonpath([normalized_path, normalized_root])
        return common == normalized_root
    except Exception:
        return False


def _should_include(file_path: str, include_extensions: Tuple[str, ...]) -> bool:
    _, ext = os.path.splitext(file_path)
    return ext.lower() in include_extensions


def find_files(config: FileDiscoveryConfig | str) -> Iterator[str]:
    """Yield file paths under root matching configured extensions.

    Args:
        config: Either a root directory (str) or a FileDiscoveryConfig.

    Yields:
        Absolute file paths.
    """

    if isinstance(config, str):
        config = FileDiscoveryConfig(root=config)

    for current_root, dirs, files in os.walk(
        config.root, followlinks=config.follow_symlinks
    ):
        # mutate dirs in-place to control traversal
        dirs[:] = [
            d for d in dirs if d not in config.exclude_dirs and not d.startswith(".")
        ]

        for file_name in files:
            if file_name.startswith("."):
                continue
            abs_path = os.path.join(current_root, file_name)
            if _should_include(abs_path, config.include_extensions):
                yield os.path.realpath(abs_path)


def read_text_file(path: str, encoding: str = "utf-8") -> str:
    """Read a text file robustly with UTF-8 default and CRLF handling.

    Returns content with normalized newlines ("\n").
    """

    with open(path, "r", encoding=encoding, errors="replace", newline="") as f:
        data = f.read()
    # Normalize newlines
    return data.replace("\r\n", "\n").replace("\r", "\n")


def relativize(path: str, start: str) -> str:
    """Return a display-friendly relative path from start to path."""

    try:
        return os.path.relpath(path, start)
    except Exception:
        return path


def ensure_within(path: str, root: str) -> Optional[str]:
    """Return normalized path if inside root; otherwise None."""

    if is_relative_to(path, root):
        return os.path.realpath(os.path.abspath(path))
    return None


def list_directory_files(directory: str) -> List[str]:
    """List files directly in a directory (non-recursive)."""

    try:
        entries = os.listdir(directory)
    except FileNotFoundError:
        return []
    files: List[str] = []
    for name in entries:
        abs_path = os.path.join(directory, name)
        if os.path.isfile(abs_path):
            files.append(abs_path)
    return files


