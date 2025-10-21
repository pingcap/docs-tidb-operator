#!/usr/bin/env python3
"""Validate Markdown docs in the repository.

Runs a suite of checks:
- Link and anchor validation
- Image reference validation

Exit codes:
 0: success, no errors
 1: errors found
 2: execution failure (invalid args, unexpected exception)
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from markdown_checks import (
    FileDiscoveryConfig,
    find_files,
    read_text_file,
    check_markdown_links,
    check_markdown_images,
    Report,
)


def _discover_targets(paths: List[str]) -> List[str]:
    files: List[str] = []
    for p in paths:
        abs_p = os.path.realpath(os.path.abspath(p))
        if os.path.isdir(abs_p):
            for f in find_files(abs_p):
                files.append(f)
        elif os.path.isfile(abs_p) and abs_p.lower().endswith(".md"):
            files.append(abs_p)
    # De-duplicate while preserving order
    seen = set()
    unique: List[str] = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate Markdown docs")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["en", "zh"],
        help="Files or directories to scan (default: en zh)",
    )
    parser.add_argument(
        "--repo-root",
        default=os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
        help="Repository root (for resolving relative links)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error output",
    )
    args = parser.parse_args(argv)

    repo_root = os.path.realpath(os.path.abspath(args.repo_root))
    targets = _discover_targets(args.paths)

    if not targets:
        if not args.quiet:
            print("No Markdown files found to validate.")
        return 0

    report = Report()

    for md_file in targets:
        try:
            link_issues = check_markdown_links(md_file, repo_root)
            img_issues = check_markdown_images(md_file, repo_root)
            report.extend(link_issues)
            report.extend(img_issues)
        except Exception as exc:
            from markdown_checks.report import Issue

            report.add(
                Issue(
                    file=md_file,
                    line=1,
                    severity="error",
                    code="EXCEPTION",
                    message=f"Exception while processing file: {exc}",
                )
            )

    if args.format == "json":
        print(report.to_json())
    else:
        text = report.to_text(base_dir=repo_root)
        if text:
            print(text)

    return 1 if report.has_errors() else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        sys.exit(2)


