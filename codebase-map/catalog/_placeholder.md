# `codebase-map/catalog/`

Empty in v1 by design. Populated in **Phase 3** of `PLAN.md`.

This will hold Backstage-format `catalog-info.yaml` entities — one per repo, mirroring what the Quarkiverse `quarkus-backstage` extension would emit at build time. Stored centrally per the no-files-in-repos constraint (see `../adr/0001-shadow-catalog-pattern.md`).

Eventual structure:

```
catalog/
  components/<repo>.yaml      kind: Component, one per repo
  apis/<api-name>.yaml        kind: API
  systems/<system>.yaml       kind: System (typically aligns with a domain)
  domains/<domain>.yaml       kind: Domain
  groups/<team>.yaml          kind: Group (teams)
  resources/<store>.yaml      kind: Resource (DBs, queues)
  all-locations.yaml          kind: Location pointing at the above
```

If/when Backstage is stood up, `all-locations.yaml` is the single Location entity that boots the entire catalog. No files need to land in any of the 232 repos.

Template for `Component` lives at `../templates/catalog-component.yaml.template`.
