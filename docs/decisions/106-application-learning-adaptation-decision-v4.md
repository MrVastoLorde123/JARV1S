# Decision 106 — Application Learning Adaptation Decision V4

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`36dd7e3bfb026826d6951e5870fd23d3170948b9` — M23.93 application-learning adaptation proposal v4.

## Purpose
M23.94 establishes the explicit advisory decision boundary immediately after M23.93 application-learning adaptation proposal v4.

A `PROPOSED` candidate becomes either `ACCEPTED` or `REJECTED` through an explicit decision input. A `BLOCKED` proposal remains `BLOCKED`, regardless of acceptance input. Decision evidence does not grant authorization or execute the proposed change.

## Contract
- Consumes exactly one M23.93 application-learning adaptation proposal v4 artifact.
- `PROPOSED` + `accept=True` → `ACCEPTED`.
- `PROPOSED` + `accept=False` → `REJECTED`.
- `BLOCKED` → `BLOCKED`, regardless of acceptance input.
- Preserves the complete proposal provenance relevant to the decision boundary, including eligibility, integrity, signal, evaluation, feedback, feedback-source, classification, application, decision, source-proposal, and outcome identities; statuses; confidence; fingerprints; failure evidence; reasons; and lineage.
- Creates a new decision identity while preserving the proposal identity.
- Does not carry forward the proposal payload as executable authority; the decision records bounded decision basis instead.
- Recursively freezes decision basis, reasons, and lineage.
- Wrong source type or blank decision ID fails closed.
- No execution status, authorization, permission, scheduling, model update, memory mutation, policy mutation, persistence mutation, or automatic action is introduced.

## Authority walls
Decision ≠ Authorization.
Decision ≠ Permission.
Decision ≠ Adaptation.
Decision ≠ Execution.
Decision ≠ Learning.
Decision ≠ Retry Permission.
Decision ≠ Scheduling.
Decision ≠ Model Update.
Decision ≠ Memory Mutation.
Decision ≠ Policy Mutation.
Decision ≠ Persistence Mutation.
Decision ≠ Truth.
Decision ≠ User Intent.

M23.94 is advisory-only. An `ACCEPTED` decision records bounded decision evidence; it does not itself authorize or execute adaptation.

## Rejection / blocking boundary
`REJECTED` and `BLOCKED` decisions remain inert evidence. They do not create execution authority or permit automatic corrective action.

## Architecture

`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Adaptation Proposal → Adaptation Decision → (future adaptation application boundary)`

M23.94 does not authorize or apply the proposed adaptation.

## Verification Plan
Focused tests cover:
- proposed + accepted decision formation;
- proposed + rejected decision formation;
- blocked proposal remains blocked;
- acceptance input cannot override blocked status;
- new decision identity and proposal provenance preservation;
- proposal payload is not carried as executable decision authority;
- recursive decision-basis/reasons/lineage immutability;
- source preservation;
- wrong-source-type rejection;
- blank decision-ID rejection;
- status contract enforcement;
- advisory and mutation authority walls;
- fingerprint and provenance preservation.

Expected focused verification: **14/14**.
Expected core regression after M23.93: **1484/1484**.

No merge is implied by this decision. Local verification must be completed before this record is marked IMPLEMENTED / VERIFIED / COMPLETE.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.93.
