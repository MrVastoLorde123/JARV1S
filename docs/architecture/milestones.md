# JARVIS Milestone Architecture

This document describes the current architectural progression. Future milestone names are directional and may be refined before implementation; the boundaries below are the important part.

## M6 — Working Context

M6 established the provider-neutral working context runtime and its composition, source selection, resolution, refresh, and consumption boundaries.

```text
Sources → Selection → Resolution → Composition → WorkingContext → AIRequest
```

## M7 — Deterministic Authority

M7 established the deterministic semantic authority pipeline and ends at an execution-ready handoff.

```text
Reason → Interpret → Prioritize → Propose → Validate → Policy
→ Confirm → Integrity → Authorize → Integrity → Prepare Handoff
```

**Status: CLOSED.** No M7.11 is required.

## M8 — Agency / Execution

M8 implements the downstream execution system that consumes `ExecutionRequest`.

The architectural focus is:

```text
ExecutionRequest
      ↓
Execution Runtime
      ↓
Capability / Plugin Resolution
      ↓
Controlled Invocation
      ↓
Observation + Result
      ↓
Verification / Failure State
      ↓
Context Update
```

M8 proves that JARVIS can drive authorized operations while preserving M7's authority boundary.

## M9 — Workforce / Delegation

The worker force belongs after a reliable single-action execution path exists.

```text
JARVIS
   ↓
Work Assignment
   ↓
Worker Runtime
   ├── research
   ├── browser / web
   ├── coding
   ├── automation
   ├── document work
   └── other capabilities
```

Workers are capability-bounded execution participants, not independent authorities. Their work remains constrained by JARVIS's execution and authorization architecture.

## M10 — Intelligence / Learning

M10 develops intelligence against the real operational history produced by JARVIS while preserving the authority architecture.

The learning progression is now explicit:

```text
Experience
    ↓
Evidence + Outcome
    ↓
Evaluation
    ↓
Reasoning Quality Assessment
    ↓
Feedback Signal
    ↓
Adaptation Proposal
    ↓
Explicit Acceptance
    ↓
Bounded Preference / Behavior
    ↓
Memory Candidate
    ↓
Explicit Consolidation
    ↓
Durable Knowledge
    ↓
Reliability Assessment
    ↓
RETAINED / WATCH / CONFLICTED / SUSPENDED / REVERSED / SUPERSEDED
    ↓
Intelligence Context
    ↓
Future Reasoning
    ↓
M7 Authority
```

### M10.1 — Learning / Experience Boundary

Defines immutable Experience records and provenance-bearing evidence for later evaluation.

### M10.2 — Evidence + Outcome Evaluation

Defines deterministic SUCCESS, FAILURE, MIXED, INCOMPLETE, and INCONCLUSIVE assessments from explicit evidence and outcomes.

### M10.3 — Preference / Behavior Adaptation

Defines bounded, reversible adaptation proposals. An adaptation can change non-authoritative behavior after explicit acceptance, but it cannot mutate policy, authorization, capability, objective state, or execution semantics.

### M10.4 — Memory Consolidation / Retrieval Improvement

Defines provider-neutral memory candidates derived from evaluated experience, explicit consolidation into an inspectable durable-memory view, reversal, and deterministic retrieval over accepted memories.

```text
Memory ≠ Truth
Memory ≠ Authority
Retrieval ≠ Permission
Consolidation ≠ Authorization
Relevance ≠ Certainty
```

### M10.5 — Reasoning Quality Feedback Loop

Defines a bounded feedback layer that evaluates explicit quality signals about reasoning without declaring truth. Quality is represented by immutable dimension signals, a deterministic aggregate assessment, and a derived non-authoritative feedback signal.

```text
Reasoning / Decision
      ↓
Observed Outcome
      ↓
Evidence + Evaluation
      ↓
Reasoning Quality Assessment
      ↓
Feedback Signal
      ↓
Explicit Learning / Adaptation Boundary
      ↓
Future Reasoning Context
```

### M10.6 — Learning Reliability / Reversal

Defines the reliability lifecycle for learned artifacts. Later evidence can move an artifact to `WATCH`, `CONFLICTED`, or `SUSPENDED`, and explicit lifecycle operations can `REVERSED` or `SUPERSEDED` it without deleting historical records.

```text
Learned Artifact
      ↓
New Evidence / Observation
      ↓
Reliability Assessment
      ↓
RETAINED / WATCH / CONFLICTED / SUSPENDED
      ↓
Explicit Transition
      ↓
Immutable Lineage
      ↓
Future Retrieval / Reasoning Context
```

The reliability layer changes learning eligibility and historical status only. It does not grant authority, authorization, execution rights, capabilities, or policy mutation.

### M10.7 — Intelligence Integration

Integrates bounded outputs from M10.2–M10.6 into an immutable `IntelligenceContext` for future reasoning.

```text
Evaluation
   +
Accepted Adaptation
   +
Retrieval Evidence
   +
Reasoning Feedback
   +
Reliability Status
        ↓
Intelligence Integration
        ↓
IntelligenceContext
        ↓
Future Reasoning
        ↓
M7 Authority
```

`REVERSED`, `SUSPENDED`, and `SUPERSEDED` learning is excluded from active reasoning context. Only explicitly accepted adaptations are active behavioral guidance. The context remains evidence, not authority or truth.

```text
Intelligence Context ≠ Truth
Intelligence Context ≠ Authority
Learning ≠ Permission
Relevance ≠ Certainty
Adaptation ≠ Authorization
Evaluation ≠ Intent
Reliability ≠ Truth
Integration ≠ Execution
Intelligence ≠ Unbounded Agency
```

**Status: VERIFIED / COMPLETE.**

The exact model/provider strategy remains implementation detail. JARVIS remains the system; AI remains a capability.

## M11 — Interface / Experience

M11 exposes JARVIS through replaceable interaction surfaces without making an interface the system itself.

### M11.1 — Interface Boundary

Establishes the provider-neutral boundary between external interaction surfaces and JARVIS.

```text
Voice / Text / UI / API / Other Surface
                ↓
        InterfaceRequest
                ↓
             JARVIS
                ↓
        InterfaceResponse
```

M11.1 packages interface traffic but does not interpret intent, create authority, authorize execution, mutate policy, or choose an intelligence provider.

```text
Interface ≠ JARVIS Identity
Interface ≠ Intent Interpretation
Channel ≠ Authority
Input ≠ Authorization
Response ≠ Execution
Transport ≠ Policy
Presentation ≠ Truth
Interface Provider ≠ Intelligence Provider
```

**M11.1 Status: IN PROGRESS.**

The interface layer must converge on the same JARVIS semantic pipeline regardless of whether the caller is voice, text, UI, or API.

## Architectural Direction

```text
M6  Context
 ↓
M7  Authority                    ← CLOSED
 ↓
M8  Agency / Execution           ← CLOSED
 ↓
M9  Workforce / Delegation       ← CLOSED
 ↓
M10 Intelligence / Learning      ← CLOSED
 ↓
M11 Interface / Experience       ← M11.1
```

The sequence is deliberate: first establish what JARVIS knows, then what it is permitted to do, then how it acts, then how it scales work, then how intelligence improves, and finally how the human experiences the system.
