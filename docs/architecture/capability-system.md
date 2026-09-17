# Capability System Architecture

JARVIS already treats individual capabilities as bounded declarations. The capability-system layer adds the missing relationships among those declarations.

## Model

```text
CapabilityDefinition
       ↓
CapabilityGraph
   ↙       ↓       ↘
Dependency Utility Composition
   \        ↓        /
    \   Compounding /
     \      ↓      /
      CapabilitySystem
```

## 1. Graph

A `CapabilityGraph` contains registered `CapabilityDefinition` values and explicit `CapabilityRelation` edges.

Supported relation kinds:

- `DEPENDS_ON` — a capability requires another capability as a prerequisite;
- `ENABLES` — one capability improves the availability/usefulness of another;
- `COMPOSES_WITH` — two capabilities are structurally related for higher-order composition.

The graph is immutable and inspectable.

## 2. Dependencies

`CapabilityDependencyModel` resolves:

- direct dependencies;
- transitive dependency closure;
- dependency depth;
- missing prerequisites for a declared available set.

Dependency cycles are rejected. Readiness is not authorization.

## 3. Utility

`CapabilityUtilityProfile` records normalized dimensions:

- frequency;
- impact;
- reliability;
- scalability;
- cost;
- failure rate.

`CapabilityUtilityWeights` controls the transparent score calculation. Utility is a decision signal, not a truth claim or authority source.

## 4. Composition

`CapabilityComposition` describes a higher-order capability as an ordered sequence of existing capabilities. `CapabilityCompositionModel` can determine whether all component dependencies are available.

The model contains no invocation path.

## 5. Compounding

`CapabilityCompoundingLink` answers the systems-intelligence question:

> Does capability A make capability B more useful?

A link records:

- source capability;
- target capability;
- mechanism;
- utility gain;
- confidence;
- hypothesized vs observed evidence state.

Weighted gain is `utility_gain × confidence`.

## 6. Aggregate system

`CapabilitySystem` composes all five models into one immutable analysis boundary and exposes per-capability assessments plus system summaries.

No system assessment can authorize, invoke, execute, select a provider, or create credentials.

## Design criterion

> Build capabilities that compound. Build boundaries that do not.

A technically impressive capability is not sufficient. The system should increasingly expose measurable relationships where adding one capability improves the practical usefulness of others.
