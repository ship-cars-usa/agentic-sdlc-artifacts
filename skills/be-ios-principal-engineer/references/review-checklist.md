# Principal-Level iOS / Swift Code Review Checklist

Apply by impact — crash and data-race risks first. Cite `File.swift:line` for every finding and propose the concrete fix.

## Correctness (crash sites first)

- [ ] No force-unwrap (`!`), `try!`, or implicitly-unwrapped optional that can be `nil` at runtime. Exceptions: `@IBOutlet`, a hardcoded literal `URL`/resource that is a build-time invariant — and even those should be reasoned about.
- [ ] No force-cast (`as!`) on values whose dynamic type isn't guaranteed.
- [ ] Array/collection access is bounds-safe (no `array[index]` where `index` came from outside; use `indices.contains` / `first`).
- [ ] Optionals from external boundaries (network, `UserDefaults`, JSON, KVC) handled with `guard let`/`if let`/`??`, not assumed present.
- [ ] Errors are handled on every path; no empty `catch {}` and no `try?` that silently drops a failure the caller needs to know about.
- [ ] Enums switched exhaustively without a catch-all `default` that would silently absorb a new case (so the compiler flags you when a case is added).
- [ ] Integer/Date/locale math is locale- and timezone-safe; no force `Int(string)!`; currency/measurement not done in `Double` where precision matters.
- [ ] Backgrounding / app-lifecycle: in-flight work is cancelled or finished on `scenePhase`/`applicationDidEnterBackground`; no assumption the screen is still visible when an async result returns.

## Concurrency & Threading

- [ ] All UIKit/AppKit/`UIView`/`UIViewController` mutations happen on the main thread (`@MainActor` or `DispatchQueue.main`). The Main Thread Checker would not fire.
- [ ] The main thread is never blocked: no sync network/disk I/O, no `DispatchQueue.*.sync` from main, no large `Codable` decode / image decode / regex on main.
- [ ] View models that drive UI are `@MainActor`-isolated (or mutate published state on main explicitly).
- [ ] Types crossing actor/`Task` boundaries are `Sendable` (value types, or reference types with a documented `@unchecked Sendable` locking strategy). No shared mutable reference type passed across actors unsynchronized.
- [ ] Escaping/stored closures, Combine `sink`s, and long-lived `Task`s capture `self` with `[weak self]` (one-shot `Task`s that complete are fine strong).
- [ ] `DispatchQueue.*.sync` is never called onto a queue the caller might already be on (deadlock).
- [ ] Cancellation is honored: loops/expensive work check `Task.isCancelled` / `try Task.checkCancellation()`; requests cancel on screen dismissal.
- [ ] Completion handlers are called exactly once on every path (success, every error branch, early return). No path that silently never calls back.
- [ ] No data race on shared mutable state: protected by an actor, a serial queue, or a lock — not "it's probably fine."

## Memory (ARC)

- [ ] No retain cycle: every `delegate` is `weak` (and its protocol `: AnyObject`); closure properties, Combine subscriptions, timers, and notification observers don't strongly capture their owner.
- [ ] `unowned` is used only where the lifetime is provably longer; otherwise `weak`.
- [ ] Combine subscriptions are stored (`Set<AnyCancellable>`) — not dropped (cancels immediately) and not leaked (cleared on deinit / weak self).
- [ ] Caches are bounded: `NSCache` (or explicit eviction) for images/data; memory-pressure / `didReceiveMemoryWarning` is handled for large in-memory holdings.
- [ ] Full-resolution images aren't held when a downsampled version suffices; decode/downsample is off-main.
- [ ] No large value-type copies on a hot path (profile if a big `struct`/`Array` of structs is copied per frame/row).
- [ ] `autoreleasepool` wraps tight loops that create many temporary objects.

## Performance

- [ ] No work in `cellForRowAt`/`collectionView(_:cellForItemAt:)` beyond dequeue + assignment; no sync I/O, no decode, no per-cell allocation of formatters.
- [ ] Cells reset all mutable state on reuse (no stale image/text from a recycled cell).
- [ ] Row/item sizes are cached or cheap to compute; no constraint thrashing on scroll.
- [ ] `Formatter`s (`DateFormatter`, `NumberFormatter`) and `JSONDecoder`s are reused, not constructed per call (they're expensive to create).
- [ ] SwiftUI `body` is pure and cheap — no I/O, no heavy allocation, no side effects; expensive work is in `task`/`onAppear`/the model.
- [ ] SwiftUI: `@StateObject` to own a model (not `@ObservedObject`, which re-creates it); `ForEach` has stable `id`s; observation is scoped (`@Observable` or split models) so a small change doesn't invalidate a large view.
- [ ] No synchronous `UserDefaults`/file/Keychain access on the main thread in a hot path.

## Networking & Data

- [ ] Every request has a timeout; no reliance on the long default.
- [ ] Response decoding happens off the main thread; UI update hops back to `@MainActor`.
- [ ] Network/clock/persistence is injected (protocol or closure), not `URLSession.shared`/`Date()` hardcoded — so it's testable and mockable.
- [ ] Core Data / file I/O uses background contexts; the view context is touched only on main; saves don't block UI.
- [ ] Pagination on every unbounded list; responses aren't fully buffered when they could stream.

## Architecture & Maintainability

- [ ] Layer boundaries respected: view controllers/views don't contain business logic or networking; that lives in view models / use cases / repositories.
- [ ] Dependencies point inward (UI → Domain ← Data); no UIKit import in the Domain layer.
- [ ] Singletons/global mutable state minimized; what remains is justified and thread-safe.
- [ ] Protocols earn their place (≥2 conformers or a test seam); no one-conformer protocol-for-its-own-sake.
- [ ] Names describe intent, not implementation. `manager`, `helper`, `data`, `process()` are smells.
- [ ] Access control is tight (`private`/`final` by default); no `public`/`open` wider than needed.
- [ ] No commented-out code, no dead branches, no `// TODO: fix` without a ticket.
- [ ] Tests exist for the logic/view-model layer and cover error + cancellation paths, not only the happy path.

## iOS Smell Tests (ask these of any non-trivial change)

- [ ] Could this run on a background thread and touch UIKit? (If yes — Main Thread Checker bug waiting.)
- [ ] Could this closure/`Task`/subscription outlive its owner and keep `self` alive? (If yes — leak.)
- [ ] Could a slow network leave the UI frozen behind a spinner with no timeout? (If yes — perceived hang.)
- [ ] Could a low-memory background state kill the app because of an unbounded cache/image? (If yes — jetsam.)
- [ ] Could a force-unwrap here crash on malformed/empty server data? (If yes — crash for every affected user.)
- [ ] Is there a crash breadcrumb / log that would make a production crash here debuggable? (If no — observability gap.)
- [ ] Does this work after backgrounding and returning, or on a cancelled/dismissed screen? (If unsure — lifecycle bug.)
