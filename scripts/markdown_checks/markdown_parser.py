"""Lightweight Markdown scanners to extract links, images, and headings.

This module does not aim to fully parse Markdown. Instead, it provides
simple, robust regex-based extractors that cover the common patterns used in
the TiDB Operator documentation set.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Sequence, Tuple


LINK_PATTERN = re.compile(
    r"\[(?P<text>[^\]]+)\]\((?P<url>[^)\s]+)(?:\s+\"(?P<title>[^\"]*)\")?\)",
)

IMAGE_PATTERN = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+\"(?P<title>[^\"]*)\")?\)",
)

HEADING_PATTERN = re.compile(r"^(?P<level>#{1,6})\s+(?P<text>.+?)\s*$", re.MULTILINE)


def _slugify(text: str) -> str:
    """Generate a GitHub-like slug from heading text."""

    # Lowercase, remove non-word except spaces and dashes, collapse whitespace to dashes
    text = text.strip().lower()
    text = re.sub(r"[\t\n\r]+", " ", text)
    text = re.sub(r"["'`]+", "", text)
    text = re.sub(r"[^a-z0-9\-\s]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


@dataclass(frozen=True)
class Link:
    text: str
    url: str
    title: Optional[str]
    line: int


@dataclass(frozen=True)
class Image:
    alt: str
    src: str
    title: Optional[str]
    line: int


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    slug: str
    line: int


def extract_links(content: str) -> List[Link]:
    links: List[Link] = []
    for match in LINK_PATTERN.finditer(content):
        url = match.group("url")
        # Skip inline anchors that are part of images, those are covered by IMAGE_PATTERN
        line = content.count("\n", 0, match.start()) + 1
        links.append(
            Link(
                text=match.group("text"),
                url=url,
                title=match.group("title"),
                line=line,
            )
        )
    return links


def extract_images(content: str) -> List[Image]:
    images: List[Image] = []
    for match in IMAGE_PATTERN.finditer(content):
        line = content.count("\n", 0, match.start()) + 1
        images.append(
            Image(
                alt=match.group("alt"),
                src=match.group("src"),
                title=match.group("title"),
                line=line,
            )
        )
    return images


def extract_headings(content: str) -> List[Heading]:
    headings: List[Heading] = []
    for match in HEADING_PATTERN.finditer(content):
        level = len(match.group("level"))
        text = match.group("text").strip()
        slug = _slugify(text)
        line = content.count("\n", 0, match.start()) + 1
        headings.append(Heading(level=level, text=text, slug=slug, line=line))
    # Deduplicate slugs by appending incrementing suffixes to duplicates
    slug_counts: dict[str, int] = {}
    normalized: List[Heading] = []
    for h in headings:
        count = slug_counts.get(h.slug, 0)
        slug_counts[h.slug] = count + 1
        if count == 0:
            normalized.append(h)
        else:
            normalized.append(Heading(level=h.level, text=h.text, slug=f"{h.slug}-{count}", line=h.line))
    return normalized


