# Note Export Workflow

This workflow turns a Markdown note into a shareable HTML file using the same Jekyll rendering path as the website.

## 1. Edit the Markdown note

Example note:

```bash
notes/continuous-thinking-for-streaming-video-understanding.md
```

Make sure the note has front matter:

```yaml
---
layout: note
title: Your Note Title
subtitle: Optional subtitle
author: Your Name
date: 2026-05-31
---
```

## 2. Build the site with Jekyll

Run:

```bash
bundle exec jekyll build
```

Jekyll renders the note into `_site/`. For this example, the generated page is:

```bash
_site/notes/continuous-thinking-for-streaming-video-understanding/index.html
```

## 3. Copy the rendered HTML into `share/`

```bash
mkdir -p share
cp _site/notes/continuous-thinking-for-streaming-video-understanding/index.html share/continuous-thinking-for-streaming-video-understanding.html
```

## 4. Inline local CSS

Run:

```bash
python3 scripts/inline_css.py share/continuous-thinking-for-streaming-video-understanding.html
```

This creates:

```bash
share/continuous-thinking-for-streaming-video-understanding.inlined.html
```

Use the `.inlined.html` file when sharing.

## Notes

- Math uses MathJax from a CDN, so the reader needs internet access for equations to render nicely.
- Remote CSS/fonts are left as links.
- Local CSS such as `/assets/css/main.css` is inlined when available.
- This Jekyll-based workflow is preferred because it matches the website rendering.
- `scripts/export_note_html.py` is only a fallback when Jekyll is unavailable; it will not match the website exactly.
