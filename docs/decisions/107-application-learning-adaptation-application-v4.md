# Decision 107 — Application Learning Adaptation Application V4

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`8e6d3bfdbee1c992aaf0a55d77dd6e0b5a8263e2` — M23.94 Application Learning Adaptation Decision V4.

## Purpose
M23.95 establishes the application boundary immediately after M23.94.

An `ACCEPTED` decision with a valid proposal payload may be handed to an injected learning applier. The application result becomes immutable evidence of whether that handoff succeeded. `REJECTED` and `BLOCKED` decisions remain inert.

The application boundary is explicit and fail-closed: absence of an applier or an applier failure cannot be interpreted as successful learning or adaptation.

## Contract
- Consumes exactly one M23.94 application-learning adaptation decision v4 artifact.
- `ACCEPTED` + valid mapping proposal payload + injected applier → `APPLIED`.
- `ACCEPTED` without an applier → `NOT_APPLIED` with failure evidence.
- `ACCEPTED` with an applier exception → `NOT_APPLIED` with failure evidence.
- `REJECTED` → `REJECTED` and performs no application.
- `BLOCKED` → `BLOCKED` and performs no application.
- Preserves decision, proposal, eligibility, integrity, signal, evaluation, feedback, and outcome provenance, statuses, confidence, fingerprints, failure evidence, reasons, and lineage.
- Creates a new application identity while preserving source decision and proposal identities.
- Recursively freezes application result, reasons, and lineage.
- Wrong source type or blank application ID fails closed.
- No implicit default applier, scheduler, retry authority, or persistence is introduced.

## Authority walls
Application Result ≠ Authorization.
Application Result ≠ Permission.
Application Result ≠ User Intent.
Application Result ≠ Truth.

`APPLIED` records that the injected application boundary returned successfully; it is not a claim that the model learned, memory changed, policy changed, or persistence succeeded unless those effects are independently represented by the injected applier's own evidence.

## Rejection / failure boundary
`REJECTED` and `BLOCKED` decisions are inert.
A missing applier and an applier exception both fail closed to `NOT_APPLIED`.

## Architecture

`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Adaptation Proposal → Adaptation Decision → Adaptation Application → (future durable learning-state evidence)`

M23.95 introduces the explicit application boundary but does not define a hidden learning engine or automatic persistence path.

## Verification Plan
Focused tests cover:
- accepted decisions applying through an injected applier;
- missing-applier fail-closed behavior;
- applier exception fail-closed behavior;
- rejected and blocked inertness;
- application/proposal/decision identity preservation;
- provenance and fingerprint preservation;
- payload immutability;
- result/reasons/lineage immutability;
- source preservation;
- wrong-source-type rejection;
- blank application-ID rejection;
- advisory/authority boundary semantics;
- direct evidence invariant enforcement for application status and result shape.

Expected focused verification: **17/17**.
Expected core regression after M23.94: **1484/1484**, with M23.95 expected to produce **1501/1501** after the focused suite is added.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.94.