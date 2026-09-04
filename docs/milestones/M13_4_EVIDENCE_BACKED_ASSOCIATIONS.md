# M13.4 — Evidence-Backed Associations

## Goal

Define an explicit provenance boundary that ties a knowledge relationship to source evidence without promoting that evidence into truth, fact, policy, authorization, or execution authority.

## Boundary

`EvidenceBackedAssociation` wraps an existing `Relationship` and binds one or more explicit `AssociationEvidence` records to references already present on that relationship.

The association records **why an association is grounded**. It does not decide whether the association is true.

## Evidence model

`AssociationEvidence` contains:

- `evidence_ref`
- `source`

Evidence references are bounded, unique within an association, immutable, and must already exist on the wrapped relationship.

## Invariants

- Evidence ≠ Truth
- Evidence ≠ Fact
- Association ≠ Truth
- Association ≠ Fact
- Evidence-backed ≠ Verified
- Provenance ≠ Authority
- Evidence ≠ Intent
- Evidence ≠ Authorization
- Evidence ≠ Policy
- Evidence ≠ Execution
- M13.4 does not mutate the wrapped relationship.
- M13.4 does not perform identity resolution.
- M13.4 does not merge entities.
- M13.4 does not persist evidence or relationships.
- M13.4 does not infer new relationships.

## Serialization

The projection is deterministic and JSON-compatible. `evidence_backed=True` describes the structure of the object only; it does not guarantee correctness or truth.

Serialized authority fields remain explicitly false.

## Not included

Evidence validation, contradiction handling, confidence scoring, evidence ranking, persistence, retrieval, and runtime integration remain later M13 slices.
