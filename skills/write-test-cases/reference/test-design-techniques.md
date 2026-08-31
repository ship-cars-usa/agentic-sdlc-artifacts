# Test-design techniques & edge-case catalog

Reference for the `write-test-cases` skill. The skill derives cases by applying these
techniques against the requirement/design/code — not by free-associating. Cite the
technique that produced each case in the test-case `Technique` column.

Grounding: prefer evidence-based practice — **ISTQB** test-design techniques, **ISO/IEC 25010**
quality characteristics (functional suitability, reliability, security, usability, performance,
compatibility, maintainability, portability), **OWASP Top 10** for security-sensitive features, and
**WCAG 2.x** for UI accessibility. State risks, trade-offs, and edge cases; if a correct expected
result is not derivable, raise an open question rather than inventing a fact.

## Technique selection — feature-type → techniques
Detect **all** feature types the story matches (a story usually matches several), then **combine and
deduplicate** the techniques from every matching row. Techniques 1–5 below are the core ISTQB set;
6–12 are the domain/pattern techniques this table pulls in.

| Feature type (signals in the ticket/design/code) | Techniques to apply |
|---|---|
| Forms / input fields | Equivalence partitioning · Boundary value analysis · Form-validation patterns |
| Multi-condition / rule logic (`AND`/`OR`, flags, tiers) | Decision tables |
| Workflow with states / lifecycle (status, approval, upload) | State-transition testing |
| Many configurable options / feature toggles | Pairwise (combinatorial) testing |
| UI components / screens | Accessibility checklist (WCAG) · UI-consistency vs design |
| Authentication / authorization / roles | Authentication & authorization test matrix |
| Any entity create/read/update/delete | CRUD coverage |
| Open-ended / exploratory / thin requirements | SFDPOT tour · Zero-One-Many |
| Security-sensitive (money, PII, tokens, uploads, injection surface) | Security test vectors (OWASP) |

Print the detected feature types + the combined technique list before generating, so the coverage
is auditable. Each generated case cites the one technique that produced it.

## 1. Equivalence partitioning (EP)
Split every input into classes that should behave identically; test **one representative per
class**, valid and invalid. Example — an age field `18–99`: classes `{ <18 }`, `{ 18–99 }`,
`{ >99 }`, `{ non-numeric }`, `{ empty }`. One case per class, not one per value.

## 2. Boundary value analysis (BVA)
Bugs cluster at edges. For any ordered range or limit, test **min−1, min, min+1, max−1, max,
max+1**, plus 0, empty, and the max-length/overflow value. Applies to numbers, string lengths,
list sizes, dates, pagination, money, timeouts, retry counts.

## 3. Decision tables
When the outcome depends on a **combination** of conditions (flags, roles, states), enumerate the
condition combinations and the expected action for each. Collapse impossible/duplicate rows.
Every reachable rule becomes at least one case. This is where `AND`/`OR` logic in the AC is
exercised — the prose usually only spells out the happy combination.

## 4. State-transition testing
For anything with a lifecycle (order status, session, upload, approval, payment), map
**states × events → next state**. Test each valid transition once, and the **invalid**
transitions (event fired in a state that shouldn't accept it) — those are the negative cases the
AC almost never lists.

## 5. Error guessing / negative testing
Deliberately break it: wrong type, null/empty, oversized, malformed, duplicate submit, expired
token, unauthorized role, wrong tenant, concurrent edit, network drop mid-flow, back-button /
double-click, stale cache. Each is a negative case with an explicit expected error.

## 6. Pairwise (combinatorial) testing
When a feature has **many independent options** (toggles, dropdowns, plan tiers, channels) the full
cross-product is too large to test. Pairwise covers **every pair of parameter values at least once**
— catching the overwhelming majority of interaction bugs with a fraction of the cases. Build the
pairwise set over the parameters found in the AC/design/code; add specific full-combination cases
only where a known interaction matters (cite why).

## 7. CRUD coverage
For any entity the story creates/reads/updates/deletes, cover the **full lifecycle matrix**:
create (valid + invalid), read (own / not-found / unauthorized), update (valid, partial, conflicting,
stale), delete (own / already-deleted / referenced-by-others), and list/filter/pagination. Each
operation × each permission/role that can attempt it.

## 8. Authentication & authorization test matrix
For gated features, cross **actor × resource → allow/deny**: unauthenticated, authenticated-but-
unauthorized, role A vs role B, owner vs non-owner, cross-tenant/cross-account, expired/invalid token,
and (where relevant) step-up/MFA required. Every **deny** path needs an explicit expected error/status
— these are the negative cases the AC almost never lists.

## 9. Accessibility checklist (WCAG)
For UI features: keyboard-only operation and focus order, visible focus, screen-reader labels/roles
(name/role/value), color-contrast, error messages announced and programmatically associated with
their field, no info conveyed by color alone, and respects reduced-motion. One case per applicable
check on the touched components.

## 10. Security test vectors (OWASP)
For security-sensitive surfaces: injection (SQL/NoSQL/command/template), XSS (stored/reflected),
broken access control / IDOR (access another user's id), auth/session flaws, SSRF on server-fetched
URLs, unsafe file upload (type/size/content), sensitive-data exposure in responses/logs, and rate-
limiting/brute-force on auth. Only include vectors the feature's surface actually exposes; cite the
surface (`file:line` / endpoint).

## 11. SFDPOT tour (exploratory heuristic)
For open-ended or thin requirements, tour the product along **S**tructure, **F**unction, **D**ata,
**P**latform, **O**perations, **T**ime. Each dimension prompts cases the narrow AC won't: unusual data
shapes, platform/browser variance, operational failure, time/ordering effects. Cases that reveal
undefined behavior here become open questions, not guessed results.

## 12. Zero-One-Many
For any collection/quantity, always test **zero** (empty state), **one** (singular copy/layout), and
**many** (pagination, ordering, performance, overflow) — plus the boundary just past a page. Catches
empty-state and pluralization bugs the happy-path "a few items" case hides.

## Traceability (coverage discipline, not a case-generator)
Every AC bullet and every design state must map to **≥1 test case**; every test case must trace
back to a source (AC id, Figma frame/node, or a `file:line` behavior found in the repo). A source
with no case = a coverage gap (list it). A case with no source = either an edge case (label it
`edge`) or an assumption that needs an open question.

---

## Edge-case checklist (run against every feature)
Walk this list; each item that applies becomes a test case (type `edge`) or, if the correct
behavior isn't defined anywhere, an **open question**.

- **Empty / zero / none** — no results, empty list, 0 items, blank field, first-run/empty state.
- **Boundaries** — min, max, min−1, max+1, exact-limit, off-by-one, length caps, precision/rounding.
- **Large / many** — max-length string, huge list, pagination edges, very large numbers, long names.
- **Nulls & optionals** — required-but-missing, optional-present, null vs empty-string vs whitespace.
- **Type & format** — wrong type, locale number/date formats, unicode/emoji, RTL, leading zeros,
  trailing spaces, case sensitivity.
- **Time** — timezone boundaries, DST, expiry exactly at now, clock skew, ordering by timestamp,
  past/future dates, leap day.
- **Concurrency** — double-submit, two users editing the same record, race between accept/cancel,
  idempotency of retries, out-of-order events.
- **Auth & permissions** — unauthenticated, authenticated-but-unauthorized, role A vs role B,
  cross-tenant/cross-account access, expired/invalid token, step-up required.
- **State / lifecycle** — action on an already-completed/cancelled/deleted entity, re-entry, resume
  after interruption, stale data.
- **Failure & recovery** — dependency 4xx/5xx, timeout, partial write, network drop mid-request,
  retry behavior, what the user sees on failure.
- **Money & quantities** — negative, zero, currency rounding, min/max order, overflow.
- **i18n / a11y** — translated copy, missing translation key, screen-reader labels, keyboard-only.
- **Data integrity** — duplicate, deduplication key, referential gaps, orphaned records.

---

## Open questions — behavior that cannot be extrapolated
An **open question** is a scenario the tester can construct but for which the **correct expected
result is not derivable** from the AC, the Figma designs, or the repo code. Do **not** guess an
expected result and bury the ambiguity — surface it. Typical sources:

- An error/empty/loading state the design never shows.
- A validation limit the AC implies but never quantifies ("must be reasonable", "large files").
- A combination in the decision table the AC leaves undefined.
- A concurrency/ordering outcome the code doesn't guard and the AC doesn't mention.
- A permission/role the story doesn't say whether to allow.
- A dependency-failure path with no specified user-facing behavior.
- Copy/labels/thresholds referenced but not provided.

Each open question records: the scenario, **why** the expected result can't be determined (which
source is silent), where it would sit in the test suite, and a proposed default (clearly marked as
an assumption) so a human can confirm or correct it. Where a repo Explore agent found code that
*implies* a behavior the requirements don't state, cite that `file:line` as evidence and ask whether
that implied behavior is intended.
