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
Persistent Personalization
        ↓
End-to-End Working Context
        ↓
Response Quality
```

## Slices

- M19.1 Personalization Profile — implemented
- M19.2 Preference Context Resolution — implemented
- M19.3 Behavior Adaptation Resolution — implemented
- M19.4 Personalization Integration — implemented as bounded runtime facade
- M19.5 Persistence + Reversal — implemented
- M19.6 End-to-End Personalization — implemented

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

## M19.5 Boundary

`PersonalizationStore` provides durable JSON persistence for bounded
personalization records. Persistence is idempotent for an identical signal and
rejects conflicting reuse of the same persisted identity.

Reversal marks a persisted personalization record as `REVERSED` with an
explicit reversal reference. Reversal only removes that signal from the active
personalization projection; it does not delete or mutate the source memory,
evidence, evaluation, or learning adaptation.

Persisted records remain explicitly non-authoritative and carry no policy,
authorization, or execution semantics.

## M19.6 Boundary

`PersonalizedWorkingContextRuntime` decorates the existing
`WorkingContextRuntime` seam. It combines dynamically resolved personalization
with persisted active personalization and injects the resulting signals into
the same provider-neutral `WorkingContext` consumed by the core.

The local runtime now constructs durable processors through this personalized
context runtime, so personalization participates in the same canonical
interface → session → JARVIS path used by normal requests. The core authority
chain is unchanged.

Personalization cannot route a request, authorize an action, mutate policy,
satisfy confirmation, or execute a capability.

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
- Persistence ≠ Authority
- Reversal ≠ Deletion of Source Knowledge

M19 does not alter the canonical authority chain.
