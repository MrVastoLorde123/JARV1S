# 013 — Claim / Evidence Boundary

## Status

Proposed implementation boundary for M29.

## Purpose

M29 establishes a deterministic contract that separates agent claims from independently produced evidence.

JARVIS must be able to record what an agent asserted without treating that assertion as truth. Evidence must be represented separately and evaluated by deterministic rules.

## Core rule

> An agent output is a claim. It is never evidence merely because an agent produced it.

`VERIFIED` is a deterministic system state produced from sufficient verification evidence. An agent cannot assign `VERIFIED` to its own claim.

## Records

### Claim

A claim contains:

- `claim_id`
- `task_id`
- `actor`
- claim payload
- provenance
- supporting evidence references
- verification references
- evaluation state

Claim identity is deterministic from the task, actor, payload, and provenance. Evaluation does not change claim identity.

### Evidence

Evidence contains:

- `evidence_id`
- `task_id`
- source type
- observed payload
- provenance

Evidence identity is deterministic from the task, source type, payload, and provenance.

## State semantics

The first M29 evaluator implements these deterministic rules:

```text
Agent claim with no evidence
→ UNKNOWN

Independent observation
→ SUPPORTED

Passing test/build evidence
→ VERIFIED

Failed test/build evidence
→ CONTRADICTED

Explicit contradiction evidence
→ CONTRADICTED
```

A later boundary may add explicit rejection or dispute sources without changing the separation between claim and evidence.

## Evidence precedence

Contradictory evidence takes precedence over ordinary supporting evidence.

A passing verification result is sufficient for `VERIFIED` only when no explicit contradiction or failed verification evidence is present.

No evidence may produce `VERIFIED`.

## Inertness

M29 claim/evidence records are informational and evaluative only. They cannot:

- authorize tool execution
- invoke tools
- request execution
- mutate memory
- grant permissions
- change policy
- create agent authority
- establish truth without the defined evidence path

## Immutability and provenance

Claim and evidence records are recursively immutable at the record boundary. Provenance remains attached to the originating claim or observation.

The evaluator returns explicit evidence references and verification references so later governance layers can inspect why a claim reached a state.

## Future integration

M29 is intentionally not yet integrated into the live coding worker.

Later milestones may connect tool results and verification results to this boundary, then introduce peer review, dispute handling, human escalation, and resource governance.
