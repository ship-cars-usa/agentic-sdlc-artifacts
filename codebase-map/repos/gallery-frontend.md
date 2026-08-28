---
repo: gallery-frontend
path: ~/projects/ship-cars-usa/gallery-frontend
stack: TypeScript 4.9.5 / React 18.3.1 / single-spa 5.9.3 + single-spa-react 5.1.2 / Webpack 5.75 / MUI 5.15 + @mui/lab alpha / axios 0.21.1 / react-image-gallery 0.8.7 / npm (Node >=18.13)
domain: platform
shape: single-module
last-synced-commit: f3ad1a1dd4cdf55754ba9aa25190e564c5b3d574
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# gallery-frontend

## What it is
`@ship-cars/gallery-frontend` — a single-spa app-parcel MFE in the **CTMS / LoadBoard** cohort (depends on `@ship-cars-usa/entities-frontend-package` + `globals-frontend-package`; **not** the Loadmate `lm-*` packages). It renders a **photo/media gallery** of a load's pickup and delivery images. Older single-spa-5 generation. npm-managed, `engines.node >=18.13`. Dev port 8084. Latest commit SCP-14917 (2026-07-27) enabled React Fast Refresh.

`react-image-gallery`-based carousel in a MUI `Modal`, with `intrinsic-scale` (`contain`) for aspect-fit sizing. Attachment types are grouped via `src/AttachmentGroup.ts` and filtered to pickup/delivery image groups.

## How it fits

- **Consumes API of:** attachment data via **`entities-frontend-package`** actions — `src/utils/api.ts` calls `entities-frontend-package/actions/attachments.fetchForGallery(code)` and reads normalized `Attachment` models (`entities-frontend-package/models/attachments`). There are **no axios/API modules in this repo**; all network access is delegated to the shared package (which fronts `attachment-backend`; media bytes are served via the `Attachment` model's URLs — `media-proxy` assumed but not referenced directly here).
- **Publishes events to:** none.
- **Subscribes to:** none in this repo.
- **Owns data store:** none (browser-only).

Two mount modes (`src/root.component.tsx`):
1. **Embedded parcel** — the parent passes `attachments` / `totalAttachments` (and a `renderDownloadButton`) as parcel props; `Gallery` renders them directly.
2. **Standalone by share code** — when `props.code` is set (e.g. a public share link), it `fetchGalleryData(code)` on mount, filters to Delivery/Pickup image groups, and renders with a `SingleAttachmentDownloadButton` per image.

## Build / test / run
```
npm install                 # package.json engines: Node >=18.13 (fleet standard is 22)
npm run start               # webpack serve --port 8084
npm run build:webpack       # webpack --mode=production
npm run lint / coverage     # eslint / jest 27
npm run update:carrier-packages   # bumps entities + globals shared packages to latest
```

## Key abstractions

- `Entry` — `src/shipcars-gallery.tsx` — single-spa lifecycle (`singleSpaReact`), error boundary renders "Error when mounting parcel".
- `Root` — `src/root.component.tsx` — emotion + `tss-react` cache providers, MUI `ThemeProvider` (`src/theme/mui.ts`), `react-error-boundary`; branches on `props.code` vs passed-in `attachments`.
- `Gallery` — `src/Gallery.tsx` — `React.PureComponent` wrapping `react-image-gallery` inside a MUI `Modal`; builds `ReactImageGalleryItem[]` from `Attachment[]`.
- `GalleryImage` — `src/GalleryImage.tsx` — per-slide image with `intrinsic-scale` contain-fit sizing (class component).
- `GalleryItemDescription` — `src/GalleryItemDescription.tsx` — caption/metadata per image.
- `AttachmentGroup` — `src/AttachmentGroup.ts` — `getFromType` maps attachment type → `GroupDefinition` (PickupImages / DeliveryImages / …).
- `src/utils/api.ts` — `fetchGalleryData(code)` wrapper over `entities-frontend-package` attachment actions.
- `src/components/SingleAttachmentDownloadButton.tsx` — per-image download (share-code mode).

## Don't-do-here / gotchas

- **Deprecated React lifecycles.** `Gallery` / `GalleryImage` are class components using `componentWillMount` / `componentWillReceiveProps` — unsafe under React 18 (fire warnings, will break in a future major / StrictMode double-invoke). Migrate before any React upgrade.
- **Old shadow overstated the media flow.** It claimed this MFE talks to `attachment-backend` + `media-proxy` **directly over HTTP with signed keys**. In fact all fetching goes through `entities-frontend-package` actions; there is no direct axios/API-key handling in this repo. Media-URL/expiry behavior lives in that shared package (and the backend), not here.
- **README says Node 16.x** — stale; `package.json` `engines` is `>=18.13`, and the rest of the fleet is on Node 22. Trust `package.json`, not the README.
- **`axios` 0.21.1** — old major with known CVEs (a transitive/legacy dep here; the repo itself has no direct API calls).
- **Older single-spa generation** (single-spa 5.9 / single-spa-react 5.1, Webpack 5.75, `@mui/lab` alpha) — coordinated bump needed when the shell upgrades.
- **IE-era code** — `GalleryImage` still branches on `"ActiveXObject" in window`; harmless but dead.
- **CTMS/LB cohort** — depends on `entities`/`globals` shared packages; a major bump there (as in `settings-frontend` SCP-15043) can ripple in.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/attachment-backend.md` — attachment metadata source (fronted here by `entities-frontend-package`).
- `~/projects/codebase-map/repos/media-proxy.md` — Go service serving the actual media bytes.
- `~/projects/codebase-map/repos/settings-frontend.md` — sibling CTMS/LB single-spa-5 MFE (same shared packages).
- `~/projects/codebase-map/domains/platform.md`.
