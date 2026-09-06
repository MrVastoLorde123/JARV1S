# Decision 111 — Learning-State Transition Integrity V4

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Parent
`f559e20e418de6e10a8bade483b0d10ba8fd6c93` — M23.98 Learning-State Transition V4.

## Purpose
M23.99 establishes a deterministic integrity boundary over one M23.98 learning-state transition artifact.

The boundary fingerprints the complete transition representation, preserves the transition outcome and upstream learning provenance, and emits immutable integrity evidence. Integrity validates representation continuity; it does not prove that the persisted state is correct, useful, true, authorized, or desirable.

## Contract
- Consumes exactly one M23.98 learning-state transition v4 artifact.
- Requires a non-empty integrity identity.
- Computes a deterministic SHA-256 fingerprint over the complete transition dataclass representation.
- Mapping key order is canonicalized while list/tuple order remains significant and sets are deterministically ordered.
- Preserves transition identity, evidence/provenance, state key, transition status, state payload, reasons, lineage, confidence, and application fingerprints.
- Records the computed transition fingerprint as integrity-owned evidence.
- Does not invent or claim an upstream transition fingerprint that M23.98 did not emit.
- Emits immutable `VALID` or `INVALID` integrity evidence; `INVALID` requires a failure reason.
- Recursively freezes state, reasons, and lineage representations.
- Source transition is never mutated.

## Authority walls
Transition integrity is evidence about representation continuity only.

`Transition Integrity ≠ Truth`
`Transition Integrity ≠ Correctness`
`Transition Integrity ≠ Authorization`
`Transition Integrity ≠ Permission`
`Transition Integrity ≠ Learning`
`Transition Integrity ≠ Model Update`
`Transition Integrity ≠ Policy Mutation`
`Transition Integrity ≠ Execution`

M23.99 does not retry persistence, invoke a learner, mutate durable state, update a model, mutate policy, create authorization, schedule work, execute actions, or infer correctness from a `PERSISTED` status.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → (future learning-state validation / consumption)`

M23.99 closes the representation-integrity gap immediately after the durable transition boundary.

## Verification Plan
Focused tests cover:
- valid integrity formation;
- deterministic fingerprinting;
- mapping-order normalization;
- list/tuple order preservation;
- complete transition provenance preservation;
- application fingerprint preservation;
- nested immutability;
- source preservation;
- wrong-source rejection;
- blank integrity-ID rejection;
- status enum validation;
- fingerprint shape validation;
- transition-status preservation;
- advisory/authority walls;
- no retry or mutation behavior;
- preservation of the computed fingerprint across equivalent source representations.

Expected focused verification: **19/19**.
Expected core regression after M23.98: **1544/1544**, with M23.99 expected to produce **1563/1563**.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.98.
