---
name: software-design-review
description: >
  Reviews code and software designs against established design principles, and returns triaged findings.
  Use when reviewing code or software designs that are complex or important, for clearer, easier to maintain software that avoids common mistakes.
---

# Software Design Principles: Code Review

Drawing on best-practice software design principles, evaluates code or a software design (existing or proposed), and produces a triaged list of findings with `file:line` references (without making any edits). For trivial code or making decisions during design or implementation, use `software-design-principles` as a light reference instead.

## How this skill works

Orchestrates a review through subagents. Depending on the review scale, dispatches either one reviewer for a complete review or a team of six reviewers, each focused on a single concern; the calling agent combines and triages their findings.

## Reference

Load as needed; reviewers receive their relevant subset:

- [reference/principles.md](reference/principles.md) — the 27 design principles + Foundation
- [reference/calibration.md](reference/calibration.md) — calibration table for resolving cross-concern tensions
- [reference/examples.md](reference/examples.md) — worked examples (assert vs raise, P21 direction-vs-metadata, when to extract, when performance work is justified)

## Calibrate the review scale

After identifying the evaluation surface, choose the review scale that is proportionate to the user's request and the work's scope, complexity, and consequence.

A single-reviewer dispatch is generally appropriate for focused, routine, or lower-risk work. The reviewer conducts the complete review against the principles in this skill.

Use the six-reviewer team when it will improve the review of broader, more complex, or more consequential work. Large review surfaces, system-level designs, significant architectural decisions, and work with meaningful user or operational impact are common reasons to use the team. For large reviews, focused reviewers also improve finding quality by giving each concern dedicated attention.

Apply judgement to the specific review rather than treating these examples as exhaustive rules. Both modes assess the complete review surface against the same principles; the team provides broader coverage and dedicated attention to each concern.

## Phase 1: Identify the evaluation surface

Determine what is being evaluated. Three common shapes:

- **Existing code** — paths or modules in the codebase to review.
- **A diff** — `git diff HEAD`, or a diff supplied in context.
- **A proposed change** — a code chunk or design that has not been written to disk yet.

If the user hasn't named a surface, default to recent work: run `git diff HEAD` to see uncommitted changes. If there are no git changes, review the most recently modified files the user mentioned or that were edited earlier in this conversation. Ask the user if these defaults yield nothing, or if the surface to review is unclear.

If the review scope or scale is uncertain, state the proposed evaluation surface and whether a single reviewer or the team is recommended, then confirm with the user before dispatching. Prefer a single reviewer when it appears sufficient.

## Phase 2: Dispatch reviewer(s)

For a single-reviewer dispatch, send one subagent the full evaluation surface, all six concern areas below, and pointers to `reference/principles.md` and `reference/calibration.md`. It conducts the complete review and returns findings in the uniform format.

For a team review, dispatch all six reviewers in parallel. Pass each subagent:

1. The full evaluation surface (paths, diff content, or proposed change).
2. The corresponding briefing file: `reviewers/<concern>.md` (read it and include the content in the subagent's prompt; or instruct the subagent to read it).
3. Pointers to `reference/principles.md` and `reference/calibration.md` so they can cross-reference.

The reviewers and their concerns:

| Concern | Briefing | Looks for |
|---|---|---|
| Premise & verification | [reviewers/premise.md](reviewers/premise.md) | Guards/abstractions whose factual premise is unverified; redundant validation; principle-citation tunnel vision |
| Structural design | [reviewers/structural.md](reviewers/structural.md) | Dependency direction, layering, module boundaries, knowledge duplication, persistence leaks, misplaced seams where the codebase already has a canonical home |
| Code-level smells | [reviewers/code-smells.md](reviewers/code-smells.md) | Speculative abstraction, mixed abstraction, redundant state, unnecessary wrappers, nested conditionals, naming, primitive obsession, magic constants, parameter shape, local codebase reuse |
| Efficiency & costs | [reviewers/efficiency.md](reviewers/efficiency.md) | Requirement-driven performance issues, repeated work, chatty expensive boundaries, unnecessary serialisation, retained state and unbounded growth, premature tuning |
| Defensive coding & hacks | [reviewers/defensive.md](reviewers/defensive.md) | Retry/sleep masking, broad except, defensive layers without a real boundary |
| Verification & completion | [reviewers/completion.md](reviewers/completion.md) | Tests, stubs (`TODO`/`NotImplementedError`/`pass`), hallucinated APIs, claiming done without observed behaviour |

Each reviewer returns findings in a uniform table:

| file:line | concern | finding | calibration anchor | proposed fix |

If a reviewer finds nothing, it returns `No findings.`

## Phase 3: Triage

Wait until every dispatched reviewer has completed.

The review converges through three consistently named outputs:

- **Findings** — issues to resolve for the reviewed work to meet its stated goal.
- **What's done well** — positive, calibrated choices worth preserving.
- **Related follow-ups** — meritorious adjacent work directly revealed by the review, but not required for the current work to converge.

Use judgement and the relationship to the current goal to decide where an observation belongs. Then:

1. **Aggregate** every returned candidate finding and positive observation into a working set, preserving its evidence and concern tags.
2. **De-duplicate** observations about the same issue or choice. Keep one consolidated entry and retain every applicable concern tag. For team reviews, note reviewer convergence as a confidence signal: convergence from 4+ reviewers is strong evidence, while a lone reviewer's finding warrants a re-check against the code.
3. **Resolve cross-concern tensions** using [reference/calibration.md](reference/calibration.md). Example: a "speculative abstraction" finding from code-smells may conflict with a "stability boundary" finding from structural — the row "Reduce coupling vs avoid abstraction" decides which applies. Also surface order-of-operations dependencies (e.g. "fix H1 first, then re-check whether M3 is still needed").
4. **Self-check** the consolidated candidate findings before classifying them:
   - For every guard/validation finding: was the call path traced?
   - For every extraction/abstraction finding: is the second-caller threshold met *and* is the "same rule" claim explicit and falsifiable?
   - For every "reuse existing code" finding: did the reviewer name the existing utility/module and confirm it owns the same rule, not just a similar shape?
   - For every efficiency finding: is there a stated requirement, an intrinsically expensive boundary, an avoidable repeated cost, unnecessary serialisation, or concrete evidence that the path matters?
   - For every principle citation: does it apply to *this exact* code, or did the reviewer reach for the closest match?
   - Remove or revise any finding that fails these checks.
5. **Classify for convergence**:
   - Place an observation in **Findings** when resolving it is needed for the reviewed work to meet its stated goal, including a gap, contradiction, unclear contract, or unmet design, verification, or behavioural requirement.
   - Classify by whether the reviewed work is complete and coherent without the change, rather than by whether the change would be valuable.
   - For each candidate **Related follow-up**, ask: “Is this worth doing now to deliver a sound reviewed result?” A yes means it belongs in **Findings**.
   - Use **Related follow-ups** for independent improvements that remain worthwhile after the reviewed work has converged. Deferring them leaves the reviewed result sound.
   - When adjacent work blocks a sound resolution of a current finding, capture the blocking issue in **Findings**.
6. **Curate What's done well** — aggregate and de-duplicate the reviewers' positive observations, including calibration already done correctly. Treat these as review evidence, not optional praise: name the concrete choice, why it is well calibrated, and what is worth preserving. An empty set is a signal to re-check the review surface and reviewer output; if none are supported after that re-check, say so without manufacturing praise.
7. **Triage** by priority:
   - **High** — real bug, user-visible failure mode, or violates a load-bearing invariant.
   - **Medium** — concrete design or verification problem that materially weakens the work's ability to meet its goal.
   - **Low** — bounded, lower-impact issue whose resolution is still needed for the work to fully meet its goal.
8. **Assign confidence** to each Finding from the direct evidence that remains after the self-check. For team reviews, include the convergence count. Treat convergence as a signal rather than a vote: 4+ reviewers is strong supporting evidence, while a lone reviewer calls for a re-check; direct code evidence may still justify high confidence without convergence.
9. **Present** exactly these sections:
   - `## Findings` — group Findings by priority with brief rationale. Retain the precise location, concern tags, finding, calibration anchor, and proposed fix; include confidence and, for team reviews, convergence count. Show order-of-operations dependencies where relevant.
   - `## What's done well` — report the concrete calibrated choices worth preserving.
   - `## Related follow-ups` — use a small table with columns for opportunity, concrete benefit, and why it is independent scope.
   Briefly note any notable candidate observation that was not carried forward, and why, under Findings rather than creating another output category.

If there are no Findings, say in one line under `## Findings` that the reviewed work is clean relative to its stated goal. If either other section has no supported entries, state `None identified.`

## The Point

> Make the system honest about what it is, ignorant of what it doesn't need to know, easy to verify, and cheap to change. Pay attention to the parts likely to change; hide them behind stable interfaces; let the rest be simple. Ship in small steps and verify by observing, not by believing.
