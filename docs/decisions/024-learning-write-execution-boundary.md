# Decision 024 — Learning Write Execution Boundary

## Context

M22.18 determines whether a `LearningWriteProposal` is admissible for a later writer. The next boundary must convert that admitted proposal into a controlled write request and an explicit immutable result without collapsing admission into execution or confusing learning writes with ordinary tool execution.

## Decision

Introduce a provider-neutral `LearningWriteExecutionService` that accepts an `ADMITTED` `LearningWriteAdmission` plus its exact `LearningWriteProposal` and delegates the mutation to a replaceable `LearningWriter`.

The execution layer:

- requires explicit admission;
- binds admission, proposal, decision, and candidate identities;
- creates a deterministic learning-write execution identity;
- passes only an immutable request to the writer;
- converts writer exceptions into an explicit failed result;
- returns an immutable result that distinguishes completion from failure;
- remains separate from tool authorization and ordinary capability execution.

The writer is the mutation mechanism. The execution service is the boundary around that mechanism, not a new authorization system.

## Boundary

```text
LearningWriteProposal
↓
LearningWriteAdmissionService
↓
LearningWriteAdmission
↓
LearningWriteExecutionService
↓
LearningWriteExecutionRequest
↓
LearningWriter
↓
LearningWriteExecutionResult
↓
Learning State / Memory
```

## Authority walls

- Learning Write Admission ≠ Learning Write Execution
- Learning Write Execution ≠ Authorization
- Learning Write Execution ≠ Tool Execution
- Learning Write Execution Result ≠ Learning Truth
- Learning ≠ Authority
- Completion ≠ Certainty

## Explicit exclusions

This milestone does not grant authorization, invoke capability policy, bypass sandbox boundaries, retry failed writes, revoke permissions, or define the concrete persistent learning stores. Domain-specific writers remain separately controlled components.
