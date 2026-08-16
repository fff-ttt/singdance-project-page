#!/usr/bin/env python3
"""Validate the self-contained SingDance static-site release."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


GITHUB_FILE_LIMIT = 100 * 1024 * 1024
LOCAL_PATH_PATTERNS = (
    re.compile(r"/(?:mmu-audio-ssd|m2v_ssd|home)/", re.IGNORECASE),
    re.compile(r"[A-Za-z]:\\"),
)


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.anchors: list[str] = []
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)

        href = values.get("href")
        if tag == "a" and href and href.startswith("#"):
            self.anchors.append(href[1:])

        for attribute in ("href", "src", "poster"):
            value = values.get(attribute)
            if not value or value.startswith(("#", "http:", "https:", "mailto:", "data:", "javascript:")):
                continue
            path = unquote(value.split("#", 1)[0].split("?", 1)[0])
            if path:
                self.references.append(path)


def validate(site_dir: Path) -> list[str]:
    errors: list[str] = []
    index = site_dir / "index.html"
    if not index.is_file():
        return [f"missing entry point: {index}"]

    html = index.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)

    duplicate_ids = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
    if duplicate_ids:
        errors.append(f"duplicate HTML ids: {', '.join(duplicate_ids)}")

    broken_anchors = sorted(set(parser.anchors) - set(parser.ids) - {""})
    if broken_anchors:
        errors.append(f"broken anchors: {', '.join('#' + item for item in broken_anchors)}")

    for reference in sorted(set(parser.references)):
        candidate = site_dir / reference
        if not candidate.is_file():
            errors.append(f"missing referenced asset: {reference}")

    files = [path for path in site_dir.rglob("*") if path.is_file()]
    for path in files:
        relative = path.relative_to(site_dir)
        if "source_clips" in relative.parts:
            errors.append(f"recoverable source clip included in public site: {relative}")
        if path.stat().st_size >= GITHUB_FILE_LIMIT:
            errors.append(f"file reaches GitHub's 100 MiB limit: {relative}")

    text_suffixes = {".html", ".css", ".js", ".json", ".md", ".txt", ".xml", ".yml", ".yaml"}
    for path in files:
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in LOCAL_PATH_PATTERNS:
            if pattern.search(text):
                errors.append(f"absolute local path found in {path.relative_to(site_dir)}")
                break

    referenced = {Path(item).as_posix() for item in parser.references}
    actual_assets = {
        path.relative_to(site_dir).as_posix()
        for path in files
        if path.relative_to(site_dir).parts[0] == "assets"
    }
    unreferenced_assets = sorted(actual_assets - referenced)
    if unreferenced_assets:
        errors.append("unreferenced public assets: " + ", ".join(unreferenced_assets))

    total_bytes = sum(path.stat().st_size for path in files)
    print(
        f"site={site_dir} files={len(files)} references={len(referenced)} "
        f"size_mib={total_bytes / 1024 / 1024:.2f}"
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site_dir", nargs="?", default="site", type=Path)
    args = parser.parse_args()

    errors = validate(args.site_dir.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("validation=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
