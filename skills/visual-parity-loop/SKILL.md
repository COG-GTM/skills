---
name: visual-parity-loop
description: >
  Efficient visual-parity workflow for UI migrations and redesigns. Use when
  comparing a reference app with a target app, reducing screenshot diffs, or
  preserving an existing UI during a framework migration. Prevents expensive
  full-matrix recaptures after every small style change.
---

# Visual Parity Loop

Match the target UI to the reference efficiently without changing product behavior.

## Establish the contract

Before editing, identify:

- Reference and target app locations.
- Routes, states, fixtures, themes, and authenticated views in scope.
- Required desktop and mobile viewports.
- The accepted mismatch threshold. Use the user's value; if none exists, propose
  `<= 2%` and state that it is a working threshold, not a claim of pixel identity.
- Functional behaviors that must remain unchanged.

Create a compact matrix:

```text
route/state | viewport | reference capture | target capture | mismatch | status
```

Do not expand the matrix beyond user-visible states needed to prove parity.

## Prepare once

1. Start the reference and target servers in separate persistent shells.
2. Pin their ports and verify both URLs before capturing.
3. Reuse one persistent browser context per app where practical.
4. Freeze dynamic data with fixtures, request interception, or a stable seed.
5. Capture the full baseline matrix once.
6. Store a reusable screenshot/diff command or script. Do not keep rewriting
   throwaway browser snippets for each selector.

## Iterate narrowly

1. Rank failures by mismatch and fix the largest structural difference first.
2. Select one failing route/state and one viewport.
3. Inspect layout and computed styles for the smallest relevant component tree.
4. Batch related changes such as typography, spacing, dimensions, and colors.
5. Re-capture only the active target view and compare it with its existing
   reference capture.
6. Repeat until that view meets the threshold, then move to the next failure.

Do not rerun the full matrix during this loop unless a shared shell, global
stylesheet, or layout primitive changed in a way that plausibly affects every view.

## Final verification

After all targeted views pass:

1. Run the full matrix exactly once.
2. Recheck functional golden paths: navigation, forms, loading/error states,
   responsive behavior, themes, and persisted settings.
3. Delegate the final UI run to the testing agent when one is available.
4. Save the final report, full screenshots, and recording requested by the user.

## Stop rules

- Stop visual tuning when every required view meets the agreed threshold.
- Do not chase anti-aliasing or rendering-engine noise below the threshold.
- Never hide content, remove functionality, hardcode fixture output, or alter
  semantics solely to reduce the visual diff.
- If the reference itself is inconsistent across runs, stabilize it before editing
  the target.
- If a required state cannot be reached, mark it untested and explain the blocker.

## Completion checklist

- [ ] Ports and server commands were stable throughout the run
- [ ] Dynamic data was deterministic
- [ ] Iteration used targeted captures rather than repeated full matrices
- [ ] The final full matrix was run after the last shared-style change
- [ ] Functional behavior was checked separately from screenshot similarity
- [ ] Remaining mismatches and untested states were reported precisely
