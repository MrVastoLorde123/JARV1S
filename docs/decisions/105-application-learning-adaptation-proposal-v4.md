# Decision 105 — Application Learning Adaptation Proposal V4

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`53eccb83f007dcd2e0413b3a2d94ce807803eaa4` — M23.92 VERIFIED / COMPLETE.

## Purpose
M23.93 establishes the advisory proposal boundary immediately after M23.92 application-learning eligibility v4.

`ELIGIBLE` application-learning eligibility evidence becomes an immutable `PROPOSED` adaptation candidate carrying an explicit mapping payload. `INELIGIBLE` evidence becomes `BLOCKED` and cannot carry an adaptation payload.

The proposal is evidence of a candidate change. It is not a decision, authorization, execution, learning-state mutation, scheduling, persistence, or truth.

## Contract
- Consumes exactly one M23.92 application learning eligibility v4 artifact.
- `ELIGIBLE` → `PROPOSED` / `ADAPTATION_CANDIDATE`.
- `INELIGIBLE` → `BLOCKED` / `BLOCKED_ADAPTATION_CANDIDATE`.
- Requires a mapping payload only for `PROPOSED` candidates.
- `BLOCKED` candidates never carry proposal payload.
- Preserves complete M23.92/M23.91/M23.90 provenance relevant to the proposal boundary, including signal, evaluation, feedback, feedback-source, classification, integrity, application, decision, proposal, outcome, eligibility identities; statuses; confidence; fingerprints; failure evidence; reasons; and lineage.
- Creates a new proposal identity while preserving the source eligibility identity.
- Recursively freezes proposal payload, reasons, and lineage.
- Wrong source type or blank proposal ID fails closed.
- Does not introduce execution status, authorization, or execution authority.

## Authority walls
Proposal ≠ Decision.
Proposal ≠ Adaptation.
Proposal ≠ Learning.
Proposal ≠ Permission.
Proposal ≠ Authorization.
Proposal ≠ Retry Permission.
Proposal ≠ Scheduling.
Proposal ≠ Execution.
Proposal ≠ Model Update.
Proposal ≠ Memory Mutation.
Proposal ≠ Policy Mutation.
Proposal ≠ Persistence Mutation.
Proposal ≠ Truth.
Proposal ≠ User Intent.

M23.93 is advisory-only. It creates a bounded candidate representation and performs no external action or state mutation.

## Rejection boundary
An `INELIGIBLE` source produces only bounded `BLOCKED` proposal evidence. It cannot create an adaptation payload or action authority.

## Architecture

`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Adaptation Proposal → (future adaptation decision/application boundary)`

M23.93 does not authorize or apply the proposed adaptation.

## Verification Plan
Focused tests cover:
- eligible evidence becoming a proposed adaptation candidate;
- ineligible evidence becoming a blocked candidate;
- required payload semantics;
- blocked payload exclusion;
- provenance and identity preservation;
- failure-evidence preservation;
- recursive immutability;
- source preservation;
- wrong-source-type rejection;
- blank proposal-ID rejection;
- status/kind consistency;
- advisory and mutation authority walls.

Verified focused verification: **15/15**.
Expected core regression after M23.92: **1455/1455**, with M23.93 expected to produce **1470/1470** after the focused suite is added.

No merge is implied by this decision. Local verification must be completed before this record is marked IMPLEMENTED / VERIFIED / COMPLETE.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.92.
