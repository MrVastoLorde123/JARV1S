# ADR-012 — Cognitive Architecture Beyond Model Wrapping

## Status

Accepted

## Context

JARVIS is intended to be a personal intelligence and agency system rather than a productized chatbot wrapper. A language model can supply valuable capabilities, but placing the model at the center of identity, memory, authority, and execution would make those boundaries fragile and provider-dependent.

JARVIS also needs to learn from experience, revise beliefs, reason under uncertainty, plan over time, and operate through tools. These properties do not require every mechanism to be implemented as machine learning.

## Decision

JARVIS will be designed as a hybrid cognitive architecture.

The system itself owns:

- persistent identity and state
- evidence and provenance
- personal knowledge and memory
- world/context representation
- cognitive orchestration
- goals and plans
- initiative
- policy and authority
- capability boundaries
- execution and recovery
- feedback and audit history

Models are replaceable cognitive capabilities inside the system.

Learning is treated as a first-class family of mechanisms rather than as a synonym for model training. The architecture supports episodic, semantic, procedural, preference, failure/outcome, belief-revision, predictive, and meta-learning.

Where useful, JARVIS will apply formal mathematical structures such as probability/Bayesian updating, graph theory, temporal reasoning, state machines, optimization, decision theory, information theory, and control/feedback systems.

A machine-learning model should be introduced when it materially improves a capability; it should not be introduced merely to label a feature as AI.

## Consequences

### Positive

- Models can be replaced without replacing JARVIS identity.
- Deterministic safety and authority contracts remain outside probabilistic model behavior.
- Learning can improve behavior without changing permissions.
- Mathematical and symbolic methods can handle classes of problems where explicit structure is stronger than learned pattern matching.
- The architecture can progressively adopt stronger ML without becoming dependent on it.

### Negative

- The system is more architecturally complex than a thin LLM wrapper.
- Learning quality must be measured across several mechanisms rather than by model benchmarks alone.
- More durable state and contracts require stronger persistence, testing, and security discipline.

## Non-negotiable boundaries

```text
Model ≠ JARVIS
Intelligence ≠ Authority
Learning ≠ Authority
Knowledge ≠ Truth
Memory ≠ User Intent
Prediction ≠ Permission
Adaptation ≠ Authorization
Initiative ≠ Authorization
Capability ≠ Permission
Planning ≠ Execution
```

## Relationship to milestones

M10 provides the initial learning/intelligence substrate.
M13–M14 provide personal knowledge and world context.
M15–M16 provide initiative and controlled self-development.
M20 provides long-horizon task state, planning, continuation, persistence, and recovery.
M21+ composes these capabilities into proactive cognition while preserving authority.
M24+ deepens learning, prediction, model selection, and self-improvement.
