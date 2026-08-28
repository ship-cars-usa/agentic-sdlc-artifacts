---
repo: website
path: ~/projects/ship-cars-usa/website
stack: Gatsby 2.x / React / gatsby-plugin-netlify-cms / gatsby-source-filesystem (Markdown-driven)
domain: platform
shape: Gatsby marketing site
last-synced-commit: cab79fccc7760fabf99e345e769b49d4b378b28b
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# website

## What it is
**`ship-cars-website`** — the **Ship.Cars marketing website** at `ship.cars` (the company's main public-facing domain). Built with **Gatsby 2.x** (released 2020; current Gatsby is 5.x — **3 majors behind**). Uses `gatsby-plugin-netlify-cms` for content editing via Netlify CMS, `gatsby-source-filesystem` for markdown content, plus standard Gatsby plugins (sitemap, sharp for images, react-helmet for SEO).

**Last commit 2022-12-19** (`Update nginx.conf`) — **3.5 years stale**. Like `documentation`, this is a frozen marketing-site artifact. Either:

1. The site is still being served but hasn't needed code-level changes in 3.5 years (content edits go through Netlify CMS without touching git), or
2. The site has been migrated to a different platform (Webflow, modern Next.js, marketing CMS, etc.) and this repo is dead.

The `nginx.conf` last-touched suggests deployment was via a custom nginx container, not Netlify hosting.

## How it fits

- **Public-facing site at `ship.cars`.** No auth, no Ship.Cars-internal API consumption.
- **Content source:** `content/` directory (markdown files edited via Netlify CMS).
- **Build artifact:** static HTML/CSS/JS deployed behind nginx.

## Build / test / run
```
npm install
npm run start          # gatsby develop
npm run build          # gatsby build
```

## Don't-do-here / gotchas

- **Possibly dead.** Verify `ship.cars`'s current hosting before assuming a commit here propagates. If the site has moved off Gatsby, this repo is fully archive.
- **Gatsby 2.x** — 3 majors behind. Bumping requires significant migration work. Don't attempt unless this is the current canonical website source.
- **`gatsby-plugin-netlify-cms`** — Netlify CMS itself reached end-of-active-development in 2023 (replaced by Decap CMS). Content workflow may have been broken by that.
- **Marketing site = public-facing brand impression.** If somehow this IS still live, any visual regression matters.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/public-root-app-frontend.md` — separate from this; the public-facing **app** at `public.ship.cars` (different from the marketing site at `ship.cars`).
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for archive on next refresh.
- `~/projects/codebase-map/domains/platform.md`.
