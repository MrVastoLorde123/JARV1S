# JARVIS

> **Third-Hand and Second-Brain**

JARVIS is a personal intelligence and agency system designed to help its user turn thoughts into words, words into plans, and plans into real-world outcomes.

JARVIS is **the system**. AI models, tools, plugins, workers, storage systems, and interfaces are capabilities inside it—not authorities over it.

## Current Milestone

**M10.1 — Learning / Experience Boundary: IMPLEMENTED — awaiting user verification**

M9 is complete. M10 begins the intelligence/learning layer without creating a second authority system.

### M9 roadmap

```text
M9.1  Worker Identity / Assignment Boundary       ✅
M9.2  Bounded Worker Runtime                      ✅
M9.3  Worker Context / Knowledge Boundary          ✅
M9.4  Worker Reporting / Result Integration        ✅
M9.5  Delegation / Coordination                   ✅
M9.6  Workforce Reliability / Recovery            ✅
M9.7  Driveability / Objective Continuation       ✅
```

### M10 roadmap

```text
M10.1  Learning / Experience Boundary              ✅ implemented
M10.2  Evidence + Outcome Evaluation               → next
M10.3  Preference / Behavior Adaptation
M10.4  Memory Consolidation / Retrieval Improvement
M10.5  Reasoning Quality Feedback Loop
M10.6  Learning Reliability / Reversal
M10.7  Intelligence Integration
```

### Learning invariant

```text
JARVIS should be capable of changing how it behaves
without being allowed to change what it is authorized to do.
```

### M10.1 experience walls

```text
Experience ≠ Truth
Experience ≠ Policy
Experience ≠ Authorization
Experience ≠ User Intent
Learning ≠ Authority
Confidence ≠ Certainty
Experience ≠ Execution
```

M10.1 defines immutable `Experience` records and an immutable conflict-aware store. Experiences preserve references, observations, outcomes, feedback, evaluation, confidence, and provenance for later learning; they do not themselves change policy, authorization, execution, or user intent.

## Road Ahead

```text
M6  Working Context            ✅
M7  Deterministic Authority    ✅ CLOSED
M8  Agency / Execution         ✅ CLOSED
M9  Workforce / Delegation     ✅ CLOSED
M10 Intelligence / Learning    → M10.1
M11 Interface / Experience
```

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Authority Architecture](docs/architecture/authority.md)
- [Agency Architecture](docs/architecture/agency.md)
- [Milestone Architecture](docs/architecture/milestones.md)
- [M7 Complete](docs/milestones/M7_COMPLETE.md)
- [M8 Complete](docs/milestones/M8_COMPLETE.md)
- [M8.6 Reliability / Recovery](docs/milestones/M8_6_AGENCY_RELIABILITY_RECOVERY.md)
- [M10.1 Learning / Experience Boundary](docs/milestones/M10_1_LEARNING_EXPERIENCE_BOUNDARY.md)
- [Architecture Decisions](docs/decisions/)
