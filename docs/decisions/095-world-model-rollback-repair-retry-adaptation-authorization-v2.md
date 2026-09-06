# M23.63 — World Model Rollback Repair Retry Adaptation Authorization v2

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Boundary
M23.63 is the first explicit authorization boundary in the v2 learning-to-adaptation chain. It consumes exactly one M23.62 adaptation-proposal validation artifact and can emit proposal-scoped authorization evidence only from an explicit external USER authority principal.

## Contract

- Consumes exactly one `EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2` artifact.
- `VALID` validation requires an explicit non-empty authority principal, `USER` authority kind, and an exact authorization scope bound to `proposal_id` and `proposal_fingerprint`.
- `BLOCKED` validation can only produce `DENIED` authorization evidence with no authority grant and no payload.
- Authorization is scoped to the exact validated proposal; it is not general or reusable authority.
- Preserves complete v2 provenance, bounded confidence, signal fingerprint, proposal payload, and validation fingerprint.
- Authorization evidence and nested scope/payload/reasons/lineage are recursively immutable.
- Source validation artifact remains unchanged.
- Invalid source type, blank authorization ID, blank authority principal, non-USER authority kind, or scope mismatch fails closed.
- No boolean, learned signal, model output, proposal field, or JARVIS-generated artifact can self-authorize.

## Authority model

At M23.63, the only authority class admitted by this boundary is:

`USER`

This is intentional. JARVIS may produce learning evidence, proposals, and validation evidence, but those artifacts are not themselves authorities. The authorization service does not infer a user decision from confidence, outcome, success, recommendation, or proposal content.

The exact authorization scope is:

`{"proposal_id": <validated proposal id>, "proposal_fingerprint": <validated proposal fingerprint>}`

This prevents an authorization artifact for one proposal from being silently reused for another proposal or altered payload.

## Authority walls

**Adaptation Authorization ≠ Broad Authority.**

**Adaptation Authorization ≠ User Intent Inference.**

**Adaptation Authorization ≠ Model Output.**

**Adaptation Authorization ≠ Learning.**

**Adaptation Authorization ≠ Proposal.**

**Adaptation Authorization ≠ Validation.**

**Adaptation Authorization ≠ Execution.**

**Adaptation Authorization ≠ Model Update.**

**Adaptation Authorization ≠ Memory Mutation.**

**Adaptation Authorization ≠ Policy Mutation.**

**Adaptation Authorization ≠ Scheduling.**

An `AUTHORIZED` artifact means only that an explicit USER principal authorized this exact validated proposal. It does not execute, schedule, persist, or apply the adaptation.

## Why this boundary exists

The chain now becomes:

`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Adaptation Proposal → Adaptation Proposal Validation → Adaptation Authorization → (future authorization integrity / execution handoff)`

M23.63 deliberately places a hard human-authority firewall between a system-generated candidate and any future mechanism capable of changing the system. The existence of a valid proposal does not authorize it, and model-derived evidence cannot become its own permission.
