# iOS Performance & Troubleshooting Playbook

For each symptom: pick the right tool, capture a baseline on a **real device in Release**, form a hypothesis the trace supports, fix the cheapest way, re-run the same trace to confirm.

General rules:
- The **simulator lies** about CPU, memory, GPU, and energy. Profile on hardware.
- **Debug (`-Onone`) lies** about speed. Profile Release.
- Capture a baseline trace before changing anything; you need it to prove the fix.

## Slow App Launch (cold start feels sluggish)

**Tool:** Instruments **App Launch** template; MetricKit `MXAppLaunchMetric` for field data; the `DYLD_PRINT_STATISTICS=1` env var for dylib load time.

**Where the time goes, in order of likelihood:**
1. Too much synchronous work in `application(_:didFinishLaunching)` / first view controller / `App.init` — SDK initialization (analytics, crash reporters, remote config) done serially and blocking first frame.
2. Heavy dependency graph / many dynamic frameworks (dylib loading) — `DYLD_PRINT_STATISTICS` shows pre-main time.
3. Expensive first-screen layout, large image decode, or a synchronous network/disk read before first frame.

**Fix:**
- Defer non-critical SDK init off the launch path (after first frame, or lazily on first use). Only what's needed to render the first screen runs synchronously.
- Make first-frame work async; show a cheap placeholder, fill in when data arrives.
- Audit third-party SDKs initialized at launch — many can be lazy.

## Scroll Hitches / Dropped Frames (jank)

**Tool:** Instruments **Animation Hitches** + **Time Profiler**; Core Animation debug options (Color Blended Layers, Color Offscreen-Rendered) on device.

**Diagnose:** record while scrolling. Hitches line up with main-thread spikes in Time Profiler — read the heaviest stack during the hitch.

**Common causes:**
1. Work in `cellForRowAt` — sync image decode, `DateFormatter`/`NumberFormatter` creation per cell, layout of a complex hierarchy, sync I/O.
2. Image decode/resize on the main thread (assigning a large `UIImage` decodes it on first display).
3. Offscreen rendering / blending — `cornerRadius + masksToBounds`, shadows without `shadowPath`, non-opaque overlapping layers (Color Blended Layers shows red).
4. Auto Layout constraint thrashing on every cell; uncached row heights.
5. SwiftUI: `body` doing expensive work, unstable `ForEach` identity forcing full rebuilds.

**Fix:** move decode/downsample and formatter creation off-main and cache them; set `shadowPath`; rasterize or precompute corner masks; cache row heights / use self-sizing carefully; give `ForEach` stable ids; make hot SwiftUI views `Equatable`.

## Memory Growth / OOM (jetsam) / Background Kill

**Tool:** Instruments **Allocations** (Mark Generation between two app states to see what accumulates) + **Leaks**; the Xcode **Memory Graph Debugger** for cycles; `vmmap --summary <pid>` and the memory gauge for footprint.

**Distinguish two failure modes:**
- **Leak (retain cycle):** memory grows and never comes back; Memory Graph shows the cycle (purple `!`). → break the cycle with `weak`/`unowned`.
- **Unbounded growth (no cycle):** a cache/array/image set that just keeps growing. → bound it (`NSCache`, eviction, downsampling), respond to memory pressure.

**Common culprits:**
- Closures / Combine `sink`s / retained `Task`s / timers / notification observers capturing `self` strongly.
- `delegate` not declared `weak`.
- Image cache holding full-resolution `UIImage`s; views/coordinators not released because a parent holds them strongly.
- Large `Codable` payloads buffered fully; `Data` blobs in `UserDefaults`.
- Core Data objects/contexts accumulating without reset.

**Fix order:** find and break cycles first (Memory Graph), then bound caches and downsample images, then reduce peak allocations (`autoreleasepool` in loops, stream instead of buffer), then handle memory-pressure notifications.

## Main-Thread Hang / Freeze / Watchdog Kill (0x8badf00d)

**Tool:** Instruments **Hangs** instrument; **Time Profiler** filtered to the main thread; `sample <pid>` for a stuck process; MetricKit `MXHangDiagnostic` from the field.

**Diagnose:** a hang is the main thread doing (or waiting on) something for too long. The sample/trace stack at the freeze names it.

**Common causes:**
1. Sync network or disk I/O on main (the classic: `Data(contentsOf: url)` with a remote URL, synchronous Keychain, large `UserDefaults`).
2. `DispatchQueue.*.sync` or a semaphore `wait()` on the main thread blocking on background work (also a deadlock risk).
3. Large `Codable` decode / JSON parse / regex / image decode on main.
4. A `@MainActor` async function that `await`s a long non-cancellable operation while the UI waits.

**Fix:** move the work off-main with structured concurrency, hop back to `@MainActor` only for the UI update; add timeouts to anything that can hang; never block main waiting on a background queue.

## Data Race / Intermittent Crash (EXC_BAD_ACCESS, corruption)

**Tool:** **Thread Sanitizer** (scheme → Diagnostics) for races; **Address Sanitizer** for memory corruption / use-after-free; **Zombie Objects** for messages to deallocated instances; **Main Thread Checker** for off-main UIKit calls.

**Diagnose:** these are non-deterministic, so reproduce under the sanitizer rather than by staring at code. TSan reports the two conflicting accesses and their stacks; Zombies names the deallocated class.

**Common causes:**
- Shared mutable state read/written from multiple queues without synchronization.
- A closure/`Task` accessing `self` after it was deallocated (combine with the leak/cycle analysis — sometimes the *fix* for a leak introduces a use-after-free if you make something `unowned` that doesn't outlive).
- UIKit touched off the main thread.

**Fix:** isolate the shared state behind an actor or serial queue; make UI work `@MainActor`; prefer `weak` over `unowned` unless the lifetime is provable.

## High Energy / Battery Drain

**Tool:** Instruments **Energy Log** (or the Energy gauge); MetricKit `MXCPUMetric`/`MXLocationActivityMetric`; Xcode Organizer **Energy** reports from the field.

**Common causes:**
- Frequent wakeups: timers, polling loops, chatty networking, retries without backoff.
- Location updates at high accuracy when not needed; background location.
- Networking in many small requests instead of batched; no use of background/discretionary transfers for non-urgent uploads.
- Animations or rendering running while offscreen/backgrounded.

**Fix:** batch and coalesce network requests; use the lowest sufficient location accuracy and stop updates when not needed; back off retries with jitter; pause work when backgrounded; use `URLSession` background/discretionary transfers for deferrable uploads.

## CLI Quick Reference

```bash
# List Instruments templates available on this machine
xcrun xctrace list templates

# Record a trace headlessly, then open the .trace bundle in Instruments
xcrun xctrace record --template 'Time Profiler' \
  --device-name 'iPhone' --launch -- /path/to/App.app
xcrun xctrace record --template 'Allocations' --attach <pid> --time-limit 30s

# Snapshot a stuck (hanging) process — stacks show what main is blocked on
sample <pid> 5 -file /tmp/hang.txt

# Leaked allocations in a running process
leaks <pid>

# Memory footprint / regions
vmmap --summary <pid>

# Pre-main dylib load time (set as a launch env var in the scheme)
DYLD_PRINT_STATISTICS=1
```

## Postmortem Notes (after any non-trivial production crash/hang)

Capture, briefly: the symbolicated stack or trace, the user actions leading up to it
(breadcrumbs), the device/OS/network conditions, the root cause (the defect, not the
proximate signal), the fix, and the *class* of issue to guard against — plus whether a
server-side feature flag / kill switch could have mitigated it before the next app
release shipped.
