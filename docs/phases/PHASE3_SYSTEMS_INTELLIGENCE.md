# Phase 3 — Systems Intelligence

## Objective

Turn the growing collection of JARVIS capabilities into an inspectable capability system where relationships, dependencies, usefulness, composition, leverage, and capability compounding are explicit.

The permanent design filter is:

> Does this capability eventually increase JARVIS's ability to create useful, measurable value for its user?

And the systems-intelligence criterion is:

> A capability should ideally make another capability more useful.

## Checkpoints

- M68 — Capability Graph
- M69 — Capability Dependency Model
- M70 — Capability Utility Model
- M71 — Capability Composition
- M72 — Capability Compounding / Leverage
- M73 — Capability System + Runtime Composition Boundary

## Architecture

```text
Capability Registry
       ↓
Capability Graph
       ↓
Dependency Model
       ↓
Utility Model
       ↓
Capability Composition
       ↓
Capability Compounding / Leverage
       ↓
Capability System Assessment
       ↓
Future prioritization / value creation
```

### Capability Graph

The graph gives declared capabilities stable identities and explicit relationships. It supports dependency, enabling, and composition relationships without introducing execution semantics.

### Dependency Model

Dependencies are resolved as direct and transitive prerequisites. Dependency cycles are rejected. Readiness is a factual structural assessment and is not permission to use a capability.

### Utility Model

Utility is represented with normalized, measurable dimensions: frequency, impact, reliability, scalability, cost, and failure rate. A configurable weight vector produces a transparent normalized utility score.

### Capability Composition

Composition describes how existing capabilities can form a higher-order capability. Components are ordered and prerequisite-aware. Composition readiness never invokes a step and never authorizes the resulting capability.

### Capability Compounding

Compounding explicitly models the relation:

```text
Capability A
    ↓ increases usefulness of
Capability B
```

Each link records the mechanism, expected/observed utility gain, and confidence. Gain is discounted by confidence so a hypothesis cannot masquerade as measured truth.

### Capability System

The aggregate system composes graph, dependency, utility, composition, and compounding models into one inspectable snapshot. It exposes cross-model assessments without creating a ranking authority or execution pathway.

## Boundaries

```text
Capability ≠ Permission
Capability ≠ Authority
Capability selection ≠ Authorization
Composition ≠ Execution
Utility ≠ Truth
Confidence ≠ Certainty
Compounding ≠ Permission
Value ≠ Authority
Learning ≠ Authority
```

Phase 3 does not create authorization, tool invocation, provider selection, persistence, credentials, or independent execution authority.

## Runtime integration

`JarvisRuntime` may accept an already-constructed `CapabilitySystem` as an injected read/analysis boundary. The runtime exposes it for inspection but continues to report that it does not authorize or execute capabilities.

## Completion gate

The phase is complete only after one consolidated local receipt covering:

1. focused Phase 3 tests;
2. Phase 3 static contract verifier;
3. UI production build;
4. full `src.core.tests` regression baseline (3279 expected, because the Phase 3 focused suite lives outside `src/core/tests`).
