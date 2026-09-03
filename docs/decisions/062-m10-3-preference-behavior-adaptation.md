# Decision 062 — M10.3 Preference / Behavior Adaptation

## Status

**ACCEPTED**

M10.3 establishes a bounded adaptation boundary above M10.1 Experience and M10.2 Evaluation.

## Decision

JARVIS may propose changes to preferences or non-authoritative behavior from explicit evaluated experience, but a proposal is not itself a behavior change. State change requires an explicit acceptance reference and remains reversible.

Adaptation state is separate from M7 policy, authorization, objectives, capabilities, and execution.

## Contract

```text
AdaptationProposal
├── proposal_id
├── kind
├── target
├── current_value
├── proposed_value
├── supporting_evaluation_ids
├── rationale
├── confidence
├── reversible
└── explicit_user_preference

AdaptationRecord
├── record_id
├── proposal
├── state
├── acceptance_reference
└── reversal_reference
```

## States

```text
PROPOSED
ACCEPTED
REJECTED
REVERSED
```

## Semantic walls

```text
Adaptation ≠ Authorization
Preference ≠ Policy
Behavior ≠ Authority
Feedback ≠ Truth
Evaluation ≠ User Intent
Learning Candidate ≠ Learned Policy
Adaptation ≠ Execution
Adaptation ≠ Self-Modification of Authority
```

## Required properties

- Every proposal has explicit identity and supporting evaluation references.
- Adaptation remains reversible.
- Explicit user preferences cannot be silently overwritten; accepting such a proposal requires an explicit acceptance reference.
- Accepted and reversed states preserve provenance through acceptance/reversal references.
- Adaptation serialization explicitly denies authority, authorization, execution, and policy mutation.
- Duplicate adaptation records are explicit conflicts.
- Adaptation does not mutate objective state, capability, policy, or M7 authorization.

## Non-goals

M10.3 does not implement model training, autonomous policy mutation, authorization, execution, capability acquisition, objective mutation, irreversible self-modification, or hidden preference changes.

## Flow

```text
Experience
    ↓
Evaluation
    ↓
Adaptation Proposal
    ↓
Explicit Acceptance
    ↓
Bounded Preference / Behavior State
    ↓
Reversible Adaptation
```

Future M10 stages may use accepted adaptations as evidence of what behavior works, but any authority-changing or executable effect must still enter the established M7–M9 boundaries.
