# M15.4 — Initiative Proposal

## Purpose

Convert an evaluated initiative candidate into a structured proposal artifact suitable for downstream validation.

## Boundary

An `InitiativeProposal` preserves lineage to exactly one `InitiativeEvaluation` and therefore to its candidate. It describes a proposed action and the reasoning supporting the proposal.

A proposal is not an instruction, authorization, policy decision, confirmation, or execution request.

## Invariants

- Proposal ≠ Instruction
- Proposal ≠ Authorization
- Proposal ≠ Confirmation
- Proposal ≠ Policy
- Proposal ≠ Execution
- Evaluation ≠ Authorization
- Relevance ≠ Obligation

## Lineage

```text
InitiativeCandidate
        ↓
InitiativeEvaluation
        ↓
InitiativeProposal
        ↓
Validation
        ↓
Policy
        ↓
Confirmation
        ↓
Authorization
```

M15.4 does not alter the existing authority chain.
