# M16.1 — Self-Development Proposal

## Purpose

Define the smallest safe artifact for JARVIS to describe a possible change to its own implementation or behavior.

## Boundary

A `SelfDevelopmentProposal` is a descriptive proposal only.

```text
Self-development proposal ≠ instruction
Self-development proposal ≠ validation
Self-development proposal ≠ policy
Self-development proposal ≠ confirmation
Self-development proposal ≠ authorization
Self-development proposal ≠ execution
Self-development proposal ≠ authority-scope change
Self-development proposal ≠ identity change authorization
```

## Required properties

Each proposal has:

- stable proposal identity
- human-readable title and description
- target area
- rationale
- expected change
- affected paths
- validation requirements
- rollback plan when reversible
- immutable bounded metadata

## Design rule

JARVIS may change how it behaves without being allowed to change what it is authorized to do.

M16.1 therefore defines the proposal object only. Modification, validation, observation, rollback, and authorization remain separate downstream concerns.

## Intended progression

```text
Inspect
  ↓
Reason
  ↓
Self-Development Proposal
  ↓
Validation Plan
  ↓
Authorization Boundary
  ↓
Modification
  ↓
Tests / Observation
  ↓
Rollback or Verify
```
