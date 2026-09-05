# Decision 028 — Learning Write Adaptation Decision Boundary

## Context

M22.22 converts learning-write feedback into an immutable adaptation candidate. The candidate is evidence about an observed write outcome, not authority or truth. JARVIS needs an explicit decision boundary before any future adaptation proposal or state change.

## Decision

Introduce `LearningWriteAdaptationDecisionService` and `LearningWriteAdaptationDecision` as a provider-neutral, non-mutating decision boundary after adaptation evaluation.

The boundary:

- consumes only an immutable `LearningWriteAdaptationCandidate`;
- produces explicit `ACCEPT`, `DEFER`, or `REJECT` semantics;
- preserves exact feedback/execution/admission/proposal/decision/source-candidate/domain lineage;
- uses deterministic decision identity in the baseline provider;
- recursively freezes metadata;
- keeps confidence bounded to [0.0, 1.0];
- rejects any attempt to grant adaptation-write authority, memory mutation authority, or execution authority.

## Baseline behavior

- observed learning-write success → `ACCEPT`;
- observed learning-write failure → `DEFER`.

This is deliberately conservative: a failed write does not itself authorize a retry or state change.

## Boundary

```text
LearningWriteFeedbackEvent
↓
LearningWriteFeedbackEvaluationService
↓
LearningWriteAdaptationCandidate
↓
LearningWriteAdaptationDecisionService
↓
LearningWriteAdaptationDecision
↓
Future Adaptation Proposal
```

## Authority walls

- Adaptation Candidate ≠ Adaptation Decision
- Adaptation Decision ≠ Adaptation Write
- Adaptation Decision ≠ Memory Mutation
- Adaptation Decision ≠ Authorization
- Adaptation Decision ≠ Retry Authorization
- Adaptation Decision ≠ Revocation
- Evaluation ≠ Authority
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

## Explicit exclusions

This milestone does not persist learning, mutate memory, authorize ordinary capability execution, retry learning writes, revoke capabilities, or define a persistent adaptation store.
