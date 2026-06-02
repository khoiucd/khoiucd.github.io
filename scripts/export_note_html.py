#!/usr/bin/env python3
"""Export a note Markdown file to a standalone HTML file."""

from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n([\s\S]*?)\n---\n?", text)
    if not match:
        return {}, text

    data: dict[str, str] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        pair = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if pair:
            key, value = pair.group(1), pair.group(2)
            if value in {">-", "|-", ">", "|"}:
                block: list[str] = []
                index += 1
                while index < len(lines) and (lines[index].startswith(" ") or not lines[index].strip()):
                    if lines[index].strip():
                        block.append(lines[index].strip())
                    index += 1
                data[key] = " ".join(block)
                continue
            data[key] = value.strip().strip("\"'")
        index += 1

    return data, text[match.end():]


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"<[^>]+>", "", slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def math_text(expr: str) -> str:
    return escape(expr)


def inline(markdown: str) -> str:
    html = escape(markdown)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    html = html.replace("&lt;sup&gt;", "<sup>").replace("&lt;/sup&gt;", "</sup>")
    html = html.replace("&lt;a href=&quot;", '<a href="').replace("&quot;&gt;", '">').replace("&lt;/a&gt;", "</a>")
    return html


def render_markdown(markdown: str) -> str:
    html_parts: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    in_table = False
    in_references = False
    lines = markdown.splitlines()
    index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            html_parts.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            html_parts.append("<ol>" + "".join(f"<li>{inline(item)}</li>" for item in list_items) + "</ol>")
            list_items = []

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            html_parts.append("</tbody></table>")
            in_table = False

    while index < len(lines):
        line = lines[index].rstrip()

        if not line.strip():
            flush_paragraph()
            flush_list()
            close_table()
            index += 1
            continue

        if line.startswith("<ol class=\"references\">"):
            flush_paragraph()
            flush_list()
            close_table()
            in_references = True
            html_parts.append('<ol class="references">')
            index += 1
            continue

        if in_references:
            if line.startswith("</ol>"):
                html_parts.append("</ol>")
                in_references = False
            else:
                html_parts.append(line)
            index += 1
            continue

        if line == "$$":
            flush_paragraph()
            flush_list()
            close_table()
            index += 1
            expr: list[str] = []
            while index < len(lines) and lines[index].strip() != "$$":
                expr.append(lines[index])
                index += 1
            html_parts.append('<div class="equation">$$\n' + math_text("\n".join(expr)) + "\n$$</div>")
            index += 1
            continue

        if line.startswith("|") and line.endswith("|"):
            flush_paragraph()
            flush_list()
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if index + 1 < len(lines) and re.match(r"^\|[\s:\-\|]+\|$", lines[index + 1].strip()):
                close_table()
                html_parts.append(
                    "<table><thead><tr>"
                    + "".join(f"<th>{inline(cell)}</th>" for cell in cells)
                    + "</tr></thead><tbody>"
                )
                in_table = True
                index += 2
                continue
            if in_table:
                html_parts.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in cells) + "</tr>")
                index += 1
                continue

        close_table()

        if line.startswith("## "):
            flush_paragraph()
            flush_list()
            title = line[3:].strip()
            html_parts.append(f'<h2 id="{slugify(title)}">{inline(title)}</h2>')
        elif line.startswith("### "):
            flush_paragraph()
            flush_list()
            title = line[4:].strip()
            html_parts.append(f'<h3 id="{slugify(title)}">{inline(title)}</h3>')
        elif re.match(r"^\d+\.\s+", line):
            flush_paragraph()
            close_table()
            list_items.append(re.sub(r"^\d+\.\s+", "", line))
        elif re.match(r"^\s*-\s+", line):
            flush_paragraph()
            close_table()
            list_items.append(re.sub(r"^\s*-\s+", "", line))
        else:
            paragraph.append(line)

        index += 1

    flush_paragraph()
    flush_list()
    close_table()
    return "".join(html_parts)


def build_html(front_matter: dict[str, str], body_html: str) -> str:
    title = front_matter.get("title", "Note")
    subtitle = front_matter.get("subtitle", "")
    author = front_matter.get("author", "")
    date = front_matter.get("date", "")
    abstract = front_matter.get("abstract", "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <script>
    window.MathJax = {{
      tex: {{
        inlineMath: [["$", "$"], ["\\\\(", "\\\\)"]],
        displayMath: [["$$", "$$"], ["\\\\[", "\\\\]"]]
      }}
    }};
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
  <style>
    body {{
      margin: 0;
      background: #faf7f0;
      color: #4a4947;
      font-family: "Iowan Old Style", Iowan, "Palatino Linotype", Palatino, Georgia, serif;
      font-size: 15px;
      line-height: 1.55;
    }}
    main {{ max-width: 760px; margin: 0 auto; padding: 40px 24px 56px; }}
    h1, h2, h3 {{ line-height: 1.2; }}
    h1 {{ font-size: 30px; margin: 0 0 6px; }}
    h2 {{ font-size: 21px; margin-top: 30px; }}
    h3 {{ font-size: 17px; margin-top: 22px; }}
    a {{ color: #8d5d45; }}
    table {{ border-collapse: collapse; width: 100%; margin: 14px 0 18px; font-size: 14px; }}
    th, td {{ border: 1px solid rgba(74,73,71,.45); padding: 6px 8px; vertical-align: top; }}
    th, strong {{ font-weight: 700; }}
    code {{ font-family: Menlo, Monaco, Consolas, monospace; font-size: .92em; }}
    .subtitle {{ font-size: 17px; margin: 0 0 6px; }}
    .meta {{ font-style: italic; margin: 0 0 18px; color: rgba(74,73,71,.78); }}
    .abstract {{ border-left: 3px solid #b17457; padding-left: 14px; margin: 18px 0 24px; }}
    .equation {{ text-align: center; font-size: 18px; margin: 16px 0; }}
    .references {{ font-size: 14px; padding-left: 22px; }}
    .references li {{ margin-bottom: 7px; }}
    sup a {{ font-size: 11px; text-decoration: none; }}
    @media print {{ body {{ background: white; }} main {{ padding: 24px; }} a {{ color: inherit; }} }}
  </style>
</head>
<body>
  <main>
    <h1>{escape(title)}</h1>
    {f'<p class="subtitle">{escape(subtitle)}</p>' if subtitle else ''}
    {f'<p class="meta">{escape(author)} · {escape(date)}</p>' if author or date else ''}
    {f'<div class="abstract"><p>{escape(abstract)}</p></div>' if abstract else ''}
    {body_html}
  </main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a note Markdown file to standalone HTML.")
    parser.add_argument("input", type=Path, help="Input Markdown note")
    parser.add_argument("-o", "--output", type=Path, help="Output HTML path")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    front_matter, body = parse_front_matter(text)
    html = build_html(front_matter, render_markdown(body))

    output = args.output or Path("share") / f"{args.input.stem}.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
