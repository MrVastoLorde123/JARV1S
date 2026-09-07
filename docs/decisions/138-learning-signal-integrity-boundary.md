# Decision 138 — Learning Signal Integrity Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`260cc57e483bd2cf30aceded0689da94a3547f24` — M23.125 Evaluation → Learning Signal Boundary.

## Purpose
M23.126 establishes the bounded integrity boundary for learning signals.

The mechanism inspects one canonical `LearningStateExecutionLearningSignal` artifact and produces immutable integrity evidence describing whether the signal is structurally and internally consistent. Integrity validation does not repair, reinterpret, learn from, authorize, or mutate the source signal.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningSignal` artifact.
- Verifies required identity fields, enum types, confidence bounds, fingerprint shape, and provenance consistency.
- Verifies evaluation, feedback, and signal lineage identifiers are mutually aligned.
- Emits explicit `VALID` or `INVALID` integrity status and preserves validation reasons.
- Preserves source signal identity and fingerprints without changing the source artifact.
- Emits recursively immutable integrity evidence.
- Does not invoke a learner or model and does not perform learning or adaptation.
- Does not establish truth, correctness, certainty, or usefulness.
- Does not authorize execution, retry, scheduling, planning, or policy mutation.
- Does not repair or rewrite malformed signal data.

## Authority Walls
`Learning Signal Integrity ≠ Learning Signal`
`Learning Signal Integrity ≠ Learning`
`Learning Signal Integrity ≠ Adaptation`
`Learning Signal Integrity ≠ Truth`
`Learning Signal Integrity ≠ Correctness`
`Learning Signal Integrity ≠ Certainty`
`Learning Signal Integrity ≠ Usefulness`
`Learning Signal Integrity ≠ Authorization`
`Learning Signal Integrity ≠ Retry Authorization`
`Learning Signal Integrity ≠ Execution`
`Learning Signal Integrity ≠ Model Update`
`Learning Signal Integrity ≠ Memory Mutation`
`Learning Signal Integrity ≠ Policy Mutation`
`Integrity Status ≠ World Truth`
`Invalid Integrity ≠ Automatic Repair`
`Valid Integrity ≠ Truth`

M23.126 protects the handoff into learning by ensuring downstream consumers can distinguish structurally coherent signal evidence from malformed signal evidence without granting the integrity layer any learning or authority powers.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Eligibility → Proposal → Decision → Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation → Learning Signal → Learning Signal Integrity → (future learning eligibility boundary)`

## Verification Plan
Focused tests cover exact source type, explicit VALID/INVALID status, structural identity requirements, provenance and cross-lineage consistency, fingerprint validation, recursive immutability, source non-mutation, deterministic construction, fail-closed invalid evidence, and absence of learning, adaptation, truth, authority, retry, execution, scheduling, planning, model, memory, or policy powers.

Local verification will be recorded here after the focused and core regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.125.
