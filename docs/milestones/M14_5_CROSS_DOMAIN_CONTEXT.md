# M14.5 — Cross-Domain Context

## Purpose

Provide a bounded, immutable composition layer that lets JARVIS view context across multiple domains without creating a second semantic or authority engine.

## Components

- `DomainReference`: descriptive reference to an object in a named domain.
- `CrossDomainLink`: explicit, evidence-referenced descriptive relationship between two domain references.
- `CrossDomainContext`: composes existing `ContextState`, `GoalProjectContext`, and `SituationalContext` with bounded references and links.

## Boundaries

```text
Cross-Domain Context ≠ Truth
Cross-Domain Link ≠ Fact
Association ≠ Inference
Cross-Domain Context ≠ User Intent
Cross-Domain Context ≠ Instruction
Cross-Domain Context ≠ Authorization
Cross-Domain Context ≠ Policy
Relevance ≠ Importance
Context ≠ Permission
```

The module is provider-neutral, immutable, bounded, serializable, and functional: adding a reference or link returns a new context rather than mutating the existing one.

## Verification

Focused coverage is provided by `src/context/tests/test_cross_domain.py`.
