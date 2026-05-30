# AGENT.md

Guidance for Codex when working in this repository.

## Project Overview

This repository is a Jekyll/Ruby personal website for Khoi Duc Nguyen, deployed through GitHub Pages at `khoiucd.github.io`.

The site is intentionally small and data-driven. The main page is:

- `index.html` - home page
- `cv.html` - cv page

Both pages render from YAML data in `_data/`. They use `layout: null` and inline their own HTML. There are no `_layouts/`, `_includes/`, or `_posts/` directories in the intended architecture.

## Commands

Use Bundler for all Jekyll commands.

```bash
bundle install
bundle exec jekyll serve
bundle exec jekyll build
```

The local development server runs at `http://localhost:4000`.

After editing `_config.yml`, restart the Jekyll server. Jekyll does not automatically reload config changes.

## Architecture

This is a data-driven, layout-free Jekyll site. Content should usually be edited in `_data/*.yml`, not directly in HTML.

When adding or changing publications, news, jobs, education, service, or experience entries, prefer editing the relevant YAML file. Only edit `index.html` or `cv.html` when changing rendering behavior, layout, or page structure.

### Data Files

- `_data/publications.yml`
  - Stores papers/publications.
  - Each entry may reference author IDs through `first_authors` and `authors`.
  - Referenced author IDs must exist in `_data/authors.yml`; missing IDs can render as blank author names.
  - Optional fields include `project_page`, `arxiv`, `github`, `video`, `open_access`, `awards`, and `highlight`.
  - `arxiv` should be the ID only. Templates build the PDF and abstract URLs.
  - `github` should use `owner/repo`.
  - `image` resolve relative to `images/`.

- `_data/authors.yml`
  - Author lookup keyed by ID.
  - The author with `is_me: true` renders without a hyperlink and receives the `author-me` CSS class.

- `_data/news.yml`
  - First five entries are shown initially.
  - Additional entries are controlled by `toggleNews()` in `js/index.js`.

- `_data/experience.yml` and `_data/services.yml`
  - Used by `index.html`.

## Configuration

`_config.yml` is the single source of truth for identity and site-wide metadata:

- name
- position
- email
- social handles
- bio/description
- Google Analytics setting

Templates should read these values from `site.*` instead of hardcoding them. The `description` field supports Markdown via `markdownify`.

## Styling

The site uses:

- Bulma vendored under `css/`
- FontAwesome
- Academicons
- Site-specific SCSS compiled by Jekyll

Main style entry points:

- `css/index.scss`
- `css/cv.scss`
- `_sass/_base.scss`

The SCSS entry files must keep the Jekyll front matter fence:

```scss
---
---
```

Without that front matter, Jekyll copies the files verbatim instead of compiling them.

## Assets

Publication figures and videos live in `images/` and are referenced by bare filename from YAML, such as `paper-image.png`.

## JavaScript

`js/index.js` handles the news show-more toggle and contains commented-out publication filter logic. There is no JavaScript build step.

## Conventions

- Do not commit generated build output such as `_site/` or `.jekyll-cache/`.
- Avoid introducing a larger Jekyll abstraction unless the site actually needs it. The current design favors simple data files and two explicit pages.
- Prefer small, focused changes that preserve the existing visual style and deployment model.

## Verification

For content-only YAML changes, run:

```bash
bundle exec jekyll build
```

For layout, SCSS, or JavaScript changes, also run the local server and inspect the affected page:

```bash
bundle exec jekyll serve
```

Check the home page when changing shared data such as publications, authors, education, or employment.
