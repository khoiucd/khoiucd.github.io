#!/usr/bin/env python3
"""Inline local CSS links in an HTML file.

This is useful after copying a Jekyll-rendered page into share/. Remote CSS
links are left unchanged by default.
"""

from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlparse


LINK_RE = re.compile(
    r"<link\b(?=[^>]*\brel=[\"']stylesheet[\"'])(?=[^>]*\bhref=[\"']([^\"']+)[\"'])[^>]*>",
    re.IGNORECASE,
)


def resolve_css_path(href: str, html_path: Path, site_root: Path) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or href.startswith("//"):
        return None

    clean_href = unquote(parsed.path)
    if clean_href.startswith("/"):
        path = site_root / clean_href.lstrip("/")
        if path.exists():
            return path
        generated_path = site_root / "_site" / clean_href.lstrip("/")
        if generated_path.exists():
            return generated_path
        return path
    return (html_path.parent / clean_href).resolve()


def inline_css(html: str, html_path: Path, site_root: Path, inline_remote: bool = False) -> str:
    def replace(match: re.Match[str]) -> str:
        href = match.group(1)
        css_path = resolve_css_path(href, html_path, site_root)

        if css_path is None:
            return match.group(0) if not inline_remote else match.group(0)

        if not css_path.exists():
            return f"<!-- Missing stylesheet: {escape(href)} -->"

        css = css_path.read_text(encoding="utf-8")
        return f"<style>\n/* Inlined from {escape(href)} */\n{css}\n</style>"

    return LINK_RE.sub(replace, html)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inline local CSS links in an HTML file.")
    parser.add_argument("input", type=Path, help="Input HTML file")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML file")
    parser.add_argument(
        "--site-root",
        type=Path,
        default=Path.cwd(),
        help="Site root used to resolve absolute local paths like /assets/css/main.css",
    )
    args = parser.parse_args()

    input_path = args.input.resolve()
    output_path = args.output or input_path.with_name(f"{input_path.stem}.inlined{input_path.suffix}")
    site_root = args.site_root.resolve()

    html = input_path.read_text(encoding="utf-8")
    output_path.write_text(inline_css(html, input_path, site_root), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
