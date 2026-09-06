# Decision 108 — Application Learning Adaptation Application Integrity V4

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`3df9b9da3295d11b19677fb12e48ac08e50f5bd2` — M23.95 Application Learning Adaptation Application V4.

## Purpose
M23.96 establishes an explicit integrity boundary over the M23.95 application artifact.

The boundary deterministically fingerprints the complete application representation and preserves the application lineage required by downstream learning-state evidence. Integrity remains evidence only.

## Contract
- Consumes exactly one M23.95 application v4 artifact.
- Requires a non-empty integrity identity.
- Computes a deterministic SHA-256 fingerprint over the complete application dataclass representation.
- Mapping key order is canonicalized without changing list/tuple order; sets are deterministically ordered.
- Preserves application, decision, proposal, eligibility, environment-integrity, signal, evaluation, feedback, classification, source-integrity, source-decision, outcome, status, and confidence provenance.
- Preserves the M23.95 application fingerprint as upstream evidence and records a separate computed fingerprint for the complete application representation.
- Emits immutable `VALID` or explicitly invalid integrity evidence; invalid evidence requires a failure reason.
- Recursively freezes reasons and lineage.
- Source application is never mutated.

## Authority walls
Integrity evidence is not truth, authorization, permission, execution, scheduling, model mutation, memory mutation, policy mutation, or persistence mutation.

`Application Integrity ≠ Application Authorization`
`Application Integrity ≠ Learning`
`Application Integrity ≠ Truth`
`Application Integrity ≠ Persistence`

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → (future durable learning-state evidence)`

M23.96 does not create durable learning state, invoke a learner, mutate memory, mutate policy, persist application state, retry application, or authorize adaptation.

## Verification Plan
Focused tests cover:
- valid application integrity formation;
- complete provenance preservation;
- upstream and computed fingerprint preservation;
- deterministic fingerprinting across mapping key order;
- nested immutability;
- source preservation;
- wrong-source-type rejection;
- blank integrity-ID rejection;
- status enum validation;
- fingerprint-shape validation;
- invalid/failure-reason invariant;
- advisory and mutation authority walls.

Expected focused verification: **12/12**.
Expected core regression after M23.95: **1501/1501**, with M23.96 expected to produce **1513/1513**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.95.
