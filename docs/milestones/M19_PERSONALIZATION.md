# M19 Personalization

## Goal

Turn persistent continuity into bounded personal assistance quality without
creating a second semantic or authority engine.

```text
Persistent Memory / Evidence
        ↓
Personalization Signals
        ↓
Personalization Profile
        ↓
Preference / Behavior Resolution
        ↓
Personalization Runtime
        ↓
Working Context / Response Quality
```

## Slices

- M19.1 Personalization Profile — implemented
- M19.2 Preference Context Resolution — implemented
- M19.3 Behavior Adaptation Resolution — implemented
- M19.4 Personalization Integration — implemented as bounded runtime facade
- M19.5 Persistence + Reversal
- M19.6 End-to-End Personalization

## M19.1 Boundary

`PersonalizationSignal` is an immutable, evidence-backed description of a
preference, behavior, or working-style pattern. `PersonalizationProfile` is an
immutable bounded collection of those signals.

The profile may inform presentation, prioritization, or other bounded behavior.
It cannot grant authority, mutate policy, authorize execution, or establish
truth.

## M19.2 Boundary

`PreferenceContextResolver` is read-only. It searches already-established
memory records, filters only `PREFERENCE` memories, preserves memory/evidence
provenance, and converts those records into profile signals.

It does not create memories, modify memories, accept adaptations, change
policy, or authorize anything.

## M19.3 Boundary

`BehaviorAdaptationResolver` is read-only. It consumes only already-accepted
M10 behavior adaptations and converts them into descriptive `BEHAVIOR`
signals. It preserves adaptation/evaluation lineage and never accepts,
rejects, reverses, or authorizes an adaptation.

## M19.4 Boundary

`PersonalizationRuntime` composes the read-only preference and behavior
resolvers with `PersonalizationContextIntegrator`. The integrator projects the
resulting profile into the existing provider-neutral `WorkingContext` as
`PERSONALIZATION` context items.

M19.4 does not yet make the core runtime implicitly personalize every request;
that end-to-end orchestration belongs to M19.6 after persistence/reversal
semantics are complete.

## Invariants

- Personalization ≠ Authority
- Preference ≠ Authorization
- Behavior ≠ Intent
- Profile ≠ Truth
- Adaptation ≠ Permission
- Learned behavior ≠ Policy
- Personalization ≠ Execution
- User model ≠ User intent
- Retrieval ≠ Mutation
- Resolution ≠ Authorization
- Context ≠ Authority

M19 does not alter the canonical authority chain.
