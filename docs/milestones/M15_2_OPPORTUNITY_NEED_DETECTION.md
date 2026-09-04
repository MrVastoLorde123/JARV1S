# M15.2 — Opportunity / Need Detection

## Purpose
Provide a bounded representation for opportunities, needs, risks, gaps, and changes detected from existing context.

## Boundary
Detection describes a possible condition. It does not establish truth, user intent, obligation, importance, authorization, policy authority, or execution permission.

## Invariants
- Detection ≠ Truth
- Detection ≠ Fact
- Detection ≠ User Intent
- Detection ≠ Obligation
- Detection ≠ Priority
- Detection ≠ Authorization
- Detection ≠ Execution

## Implementation
`src/opportunities.py` provides immutable `OpportunityDetection` values and an `OpportunityDetectionSet` collection with bounded references, deterministic membership, functional updates, and explicit non-authority serialization.
