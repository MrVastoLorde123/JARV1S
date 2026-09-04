# JARVIS Milestone Architecture

This document defines the architectural progression of JARVIS. Milestone names may evolve, but the boundaries and invariants are authoritative. The cognitive architecture introduced here applies retroactively to existing intelligence work and prospectively to M21+.

## M6 — Working Context

Provider-neutral working context runtime and context composition boundaries.

**Status: CLOSED.**

## M7 — Deterministic Authority

Established the deterministic semantic authority pipeline and execution-ready handoff.

**Status: CLOSED.**

## M8 — Agency / Execution

Established bounded execution of already-authorized operations through capabilities/plugins.

**Status: CLOSED.**

## M9 — Workforce / Delegation

Established capability-bounded workers, assignment, delegation, reporting, reliability, and bounded objective continuation.

**Status: CLOSED.**

## M10 — Intelligence / Learning

Established the first cognitive substrate: experience, evidence, outcome evaluation, preference adaptation, memory consolidation/retrieval, reasoning-quality feedback, reversal/reliability semantics, and integrated intelligence context.

M10 is no longer treated as an isolated "learning feature." It is the first explicit layer of the JARVIS cognitive architecture.

Core learning loop:

```text
Experience
  ↓
Evidence + Outcome
  ↓
Evaluation
  ↓
Reasoning Quality
  ↓
Feedback
  ↓
Adaptation
  ↓
Memory
  ↓
Reliability
  ↓
Future Reasoning
```

**Status: VERIFIED / COMPLETE.**

## M11 — Interface / Experience

Established replaceable interaction surfaces without making the interface a semantic or authority source.

**Status: VERIFIED / COMPLETE.**

## M12 — System Integration / Orchestration

Established the canonical application-facing runtime composing the existing bounded subsystems.

**Status: VERIFIED / COMPLETE.**

## M13 — Personal Knowledge

Established structured personal knowledge, identity, relationships, evidence-backed associations, persistence, and retrieval.

**Status: VERIFIED / COMPLETE.**

## M14 — Personal Context / World Model

Established bounded contextual state about the user's world.

```text
Entities + Relationships + Memories + Events + Current State + Goals + Temporal Context
                              ↓
                     Personal World Model
```

**Status: VERIFIED / COMPLETE.**

Key invariant: context may inform cognition and initiative but cannot become authority.

## M15 — Initiative / Proactive Agency

Established bounded initiative machinery: detecting opportunities/needs, evaluating candidates, forming proposals, and connecting proactive reasoning to existing authority without granting autonomous permission.

**Status: VERIFIED / COMPLETE.**

Key invariant: initiative may produce a useful proposal but cannot create authority.

## M16 — Controlled Self-Development

Established bounded machinery for JARVIS to change how it works without changing what it is authorized to do.

```text
Inspect → Reason → Plan → Modify → Test → Observe → Correct → Verify → Commit / Rollback
```

**Status: VERIFIED / COMPLETE.**

Key invariant:

```text
JARVIS may change how it works
        ≠
JARVIS may change what it is allowed to do
```

## M17 — Human Operating Layer

Makes the canonical runtime continuously usable through a human-facing operator without creating a parallel authority path.

**Status: COMPLETE / EXISTING FOUNDATION.**

## M18 — Personal Continuity

Establishes durable identity and conversation continuity across sessions and processes.

**Status: COMPLETE / EXISTING FOUNDATION.**

## M19 — Deep Personalization

Deepens adaptation of JARVIS to the user's durable preferences, patterns, context, and operating style while preserving authority boundaries.

**Status: VERIFIED / COMPLETE.**

## M20 — Long-Horizon Task Management

Establishes bounded long-horizon work representation and runtime:

```text
Goal
 ↓
Objective
 ↓
Task
 ↓
Dependency Graph
 ↓
Progress / Evidence
 ↓
Long-Horizon Plan
 ↓
Next-Step Proposal
 ↓
Persistence / Recovery
 ↓
End-to-End Runtime
```

Modules:

```text
M20.1 Goal / Objective Boundary
M20.2 Task Model / Task Lifecycle
M20.3 Dependencies / Task Graph
M20.4 Progress / State Evaluation
M20.5 Long-Horizon Planning
M20.6 Continuation / Next-Step Engine
M20.7 Persistence / Recovery
M20.8 End-to-End Long-Horizon Runtime
```

**Status: VERIFIED / COMPLETE.**

M20 is deliberately bounded: planning and continuation do not imply authorization or execution.

## M21 — Proactive JARVIS

M21 extends JARVIS from reacting to explicit requests toward bounded proactive cognition.

The updated architecture changes how M21 is built: proactive behavior is no longer treated as a simple trigger-to-action pipeline. It sits on top of the cognitive substrate established by M10, personal context from M13–M14, long-horizon state from M20, and the existing authority chain.

```text
Environment / User
        ↓
Perception / Input
        ↓
Evidence + Provenance
        ↓
Memory + Personal Knowledge
        ↓
World Model / Current Context
        ↓
Reasoning + Uncertainty
        ↓
Prediction / Evaluation
        ↓
Initiative Candidate
        ↓
Initiative Evaluation
        ↓
Proactive Proposal
        ↓
Prioritization / Value
        ↓
Validation / Policy
        ↓
Confirmation
        ↓
Authorization
        ↓
Bounded Action
        ↓
Outcome / Feedback
        └──────────────→ Learning
```

### M21.1 — Proactive Initiative Boundary

A signal may create an initiative candidate without becoming a task, proposal, authorization, notification, schedule, or execution request.

**Status: VERIFIED / COMPLETE.**

### M21.2 — Proactive Proposal Boundary

An eligible initiative candidate may be formulated into an immutable proposal that preserves candidate/trigger identity and evidence provenance. The proposal is a recommendation only.

```text
Initiative Candidate
        ↓
Eligibility
        ↓
Proposal
        ↓
[future prioritization / value assessment]
```

**Status: IMPLEMENTED / AWAITING LOCAL RECEIPT.**

### Future M21 boundaries

```text
M21.3 Prioritization / User-Value Estimation
M21.4 Information-Gain / Uncertainty Reduction
M21.5 Bounded Proactive Scheduling / Notification
M21.6 Proactive Runtime / Feedback Integration
```

These names are directional; the boundary contract remains authoritative. No M21 stage may grant authority by virtue of being proactive or predictive.

## Cross-cutting cognitive architecture

The following principles apply to all milestones, including already-complete ones and all future work.

### Intelligence is distributed

```text
Memory + Knowledge + Reasoning + Prediction + Learning + Planning + Feedback
```

No single model owns the intelligence of JARVIS.

### Model boundary

```text
Model ≠ JARVIS
LLM ≠ JARVIS
AI Provider ≠ JARVIS
Interface ≠ JARVIS
Plugin ≠ JARVIS
Worker ≠ JARVIS
```

Models are replaceable cognitive components. JARVIS owns durable state, orchestration, authority semantics, identity, and capability boundaries.

### Learning is multi-form

```text
Episodic
Semantic
Procedural
Preference
Failure / Outcome
Belief Revision
Predictive
Meta-learning
```

Learning may change future behavior and reasoning. Learning cannot grant authority.

### Mathematical mechanisms are selected by problem

```text
Probability / Bayesian reasoning → uncertainty and belief update
Graph theory                  → dependencies and relationships
Temporal reasoning            → time, validity, expiry, recurrence
State machines                → lifecycle and safety
Optimization                  → constrained prioritization
Decision theory               → risk-aware choices
Information theory            → uncertainty reduction
Control / feedback            → closed-loop correction
```

Mathematics is used as a substrate where the structure of the problem supports it; it is not added merely to appear intelligent.

### Epistemic boundaries

```text
Signal ≠ Evidence
Evidence ≠ Truth
Observation ≠ Interpretation
Interpretation ≠ Belief
Belief ≠ Prediction
Knowledge ≠ Truth
Memory ≠ User Intent
Confidence ≠ Certainty
Reliability ≠ Truth
Prediction ≠ Permission
```

### Authority boundaries

```text
Intelligence ≠ Authority
Learning ≠ Authority
Adaptation ≠ Authorization
Initiative ≠ Authorization
Capability ≠ Permission
Planning ≠ Execution
Recovery ≠ Execution
Proposal ≠ Authorization
```

### Long-term direction

M21–M25 and later milestones progressively compose cognition into a persistent personal intelligence system. Machine learning may be introduced wherever it materially improves perception, generalization, prediction, or adaptation, but it is not required for a system component to be intelligent.

The project may be described as a "pseudo-AI" only as an engineering shorthand: an intentionally constructed cognitive architecture whose intelligent behavior emerges from interacting bounded mechanisms rather than from one giant learned model.

Final security hardening remains separate from milestone semantics and will cover database isolation, filesystem boundaries, credential handling, plugin security, concurrency, process isolation, auditability, recovery, backup, secrets, and adversarial testing.
