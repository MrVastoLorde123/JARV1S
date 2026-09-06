# Decision 124 — Learning-State Semantic Use Boundary

## Status
IMPLEMENTED / PENDING LOCAL VERIFICATION

## Parent
`d3f454620ec6795e3141d1184bf4ca86b0ed8acc` — M23.111 Learning-State Semantic Use Request Boundary.

## Purpose
M23.112 establishes the first bounded semantic consumer after a validated semantic-use request. A `READY` semantic-use request may be supplied to exactly one caller-provided semantic-use function, producing immutable semantic-use evidence without treating that result as truth, correctness, certainty, learning, memory mutation, authorization, or execution.

## Contract
- Consumes exactly one canonical `LearningStateSemanticUseRequest` artifact.
- Requires request status `READY`.
- Requires a callable caller-supplied semantic-use consumer.
- Supplies only recursively frozen interpretation evidence to the consumer.
- Accepts only a mapping result as successful semantic-use evidence.
- Converts exceptions or non-mapping results into bounded `REJECTED` evidence.
- Preserves request provenance, identities, state key, fingerprints, confidence, consumer identity, and use purpose.
- Emits recursively frozen result, reasons, and lineage.
- Does not establish truth, correctness, certainty, usefulness, learning, model update, memory mutation, policy mutation, authorization, permission, scheduling, planning, or execution.
- Invokes the semantic consumer at most once per service call.

## Authority Walls
`Semantic Use ≠ Truth`
`Semantic Use ≠ Correctness`
`Semantic Use ≠ Certainty`
`Semantic Use ≠ Learning`
`Semantic Use ≠ Model Update`
`Semantic Use ≠ Memory Mutation`
`Semantic Use ≠ Authorization`
`Semantic Use ≠ Permission`
`Semantic Use ≠ Planning`
`Semantic Use ≠ Execution`

## Architecture
`... → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → (future semantic consumer / use of semantic-use evidence)`

## Verification Plan
Focused tests cover READY gating, exact request type, callable consumer validation, mapping-result acceptance, non-mapping rejection, exception rejection, single invocation, frozen input/result, provenance preservation, deterministic construction, semantic non-judgment, and absence of learning/authority/execution powers.

Local verification will be recorded here after the focused and core regression suites pass.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.111.
