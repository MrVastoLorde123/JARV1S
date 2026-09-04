# M14.7 — World-Model Integration

## Purpose

Integrate the M14 context domains behind one provider-neutral immutable facade.

## Composition

- Context state
- Temporal/history context
- Goal/project context
- Situational context
- Cross-domain context
- Explicit relevance ranking

## Boundary

World-model integration is composition, not a second reasoning engine.

- World Model ≠ Truth
- World Model ≠ Fact Store
- World Model ≠ User Intent
- World Model ≠ Instruction
- Relevance ≠ Authority
- Context ≠ Permission
- Integration ≠ Execution
- World Model ≠ Policy

## Design

`WorldModelContext` validates the types of each supplied M14 domain and offers
functional replacement methods. Existing domain objects remain unchanged and
no new inference, authorization, policy, or execution semantics are introduced.

Serialization explicitly preserves the non-authority boundary.

## Completion

M14.7 is complete only after focused tests and all context, knowledge, AI, and
core regression suites pass.
