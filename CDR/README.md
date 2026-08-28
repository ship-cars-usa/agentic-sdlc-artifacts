# Change Design Records

One folder per record. Each is fully self-contained:

```
cdr-00NN/
  index.html    the viewer + inline editor (identical across folders)
  cdr.json      the record's data (the backing file you edit)
  diagram.svg   the blast-radius graphic (edit in a vector tool)
```

## Use

1. **Open `cdr-00NN/index.html`** in a browser (double-click).
2. Click **Open folder…** and pick that record's folder (grants read/write to its files).
3. Read it, or click **Edit** to change any field, chip, or table cell **in place**; **Save** (⌘/Ctrl-S) writes `cdr.json`.

Direct in-place save needs a **Chromium** browser (Chrome / Edge / Brave / Arc) — you grant access once via the folder picker. In **Safari / Firefox** the page falls back to **Import** + **Export/download**.

Text fields accept `**bold**` and `` `code` `` shorthand.

## Records

| Folder | Status | Change |
|---|---|---|
| cdr-0007 | example | Add expedited flag to CTMS orders (illustrative, all-four-surfaces walkthrough) |
| cdr-0008 | shipped (real) | Idempotency key on carrier payment transactions |
| cdr-0009 | proposed | Add DRIVER_REASSIGNED lifecycle event (breaking) |
| cdr-0010 | shipped (real) | N-gram substring search on company name |
| cdr-0011 | proposed | Cursor-paged /v2 inventory units endpoint |
| cdr-0012 | proposed | Rename a loadboard column read cross-DB |
| cdr-0013 | accepted | GPS heading on location-log events |

Names (services, topics, DTOs, tables) are verified against source. Keep `services` matching
`codebase-map/repos/<slug>.md` so the records stay joinable to the map.

## Data shape (`cdr.json`)

`cdr`, `title`, `status`, `statusNote`, `date`, `author`, `jira`, `services[]`, `changeTypes[]`,
`diagram`, `context`, `sections[]` (each `label`, `tag`, `tables[]` → `caption`, `columns[]`
`{name, mono, change}`, `rows[]` `{change, label, cells[]}`), `detail` (`cap`, `items[][k,v,mono]`),
`rollout` (`tone`, `label`, `text`). All editable from the UI.
