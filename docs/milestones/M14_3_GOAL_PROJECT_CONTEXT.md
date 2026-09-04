# M14.3 — Goal & Project Context

## Goal

Represent goals and projects as bounded contextual state so JARVIS can understand what work matters and how goals relate to projects without turning contextual knowledge into instructions.

## Composition

```text
Goal Context       Project Context
      \                /
       \              /
        Goal & Project Context
                 ↓
          M14 World Context
```

## Contract

`GoalContext` describes a goal's contextual identity, status, optional project association, metadata, and provenance references.

`ProjectContext` describes a project's contextual identity, status, associated goal IDs, metadata, and provenance references.

`GoalProjectContext` composes these values and validates that goal/project references resolve within the supplied context.

## Invariants

- Goal Context ≠ Instruction
- Project Context ≠ Instruction
- Goal ≠ Authorization
- Goal ≠ Policy
- Project ≠ Execution Request
- Context ≠ Truth
- Context ≠ User Intent
- Status ≠ Permission
- Association ≠ Fact
- Context construction does not execute actions.
- Context construction does not grant permissions.
- Context construction does not infer missing goals or projects.

## Design

All values are immutable and bounded. Metadata is defensively frozen and provenance is explicitly retained through `source_refs`.

The integration layer validates references but does not perform identity resolution or mutate referenced entities.

## Not included

Context prioritization, situational relevance, temporal weighting, cross-domain synthesis, intent inference, proactive agency, and execution remain later M14/M15 work.
