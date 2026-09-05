# M22.2 — Capability Trust / Provenance Boundary

## Purpose

M22.2 establishes the provenance and trust-assessment boundary for JARVIS capabilities.

The boundary answers two distinct questions:

- **Provenance:** where did this capability come from, and what evidence describes that origin?
- **Trust:** what evidence-linked assessment currently exists for that capability?

Neither answer grants permission to invoke the capability.

## Contract

```text
Capability Descriptor
        ↓
Provenance Record
        ↓
Evidence
        ↓
Trust Assessment
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Execution
```

M22.2 stops at provenance and trust assessment.

## Core types

- `ProvenanceEvidence` — immutable structured evidence supporting provenance/trust claims.
- `CapabilityProvenance` — immutable origin/provenance metadata linked to a capability identity.
- `CapabilityTrustAssessment` — immutable evidence-linked trust status and bounded confidence.
- `TrustStatus` — bounded assessment outcome: `UNASSESSED`, `CONDITIONAL`, `TRUSTED`, or `UNTRUSTED`.
- `CapabilityTrustError` — bounded trust/provenance contract error.

## Invariants

- Provenance records require stable capability identity, source, origin, and integrity status.
- Optional publisher and verification-method fields, when present, must be non-empty strings.
- Provenance evidence is structured and immutable.
- Trust assessments require a stable capability identity and bounded confidence in `[0, 1]`.
- `UNASSESSED` trust must carry zero confidence.
- Non-`UNASSESSED` trust assessments require supporting evidence.
- Trust assessments may only be validated against matching capability identity.
- Provenance and trust assessment context is metadata only.
- Trust is an assessment, not a permission decision.
- Existing authority, policy, confirmation, authorization, and execution boundaries remain unchanged.

## Authority walls

```text
Provenance ≠ Trust
Trust ≠ Permission
Trust ≠ Authorization
Evidence ≠ Truth
Confidence ≠ Certainty
Assessment ≠ Execution
Capability ≠ Permission
Registration ≠ Trust
```

## Deliberate exclusions

M22.2 does not:

- execute a plugin or capability;
- grant permission;
- create authorization;
- infer execution authority from trust status;
- mutate policy;
- schedule or notify;
- select or assign a worker;
- treat provenance as proof of truth;
- automatically convert a trust assessment into an execution decision.

## Verification

Remote implementation status: **VERIFIED / COMPLETE**.

Local verification receipt: **9/9 M22.2 focused + 8/8 M22.1 focused + 487/487 core tests passed locally.**
