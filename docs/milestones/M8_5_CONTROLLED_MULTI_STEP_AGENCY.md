# M8.5 — Controlled Multi-Step Agency

**Status:** IMPLEMENTATION IN PROGRESS

## Purpose

M8.5 introduces bounded multi-step agency: JARVIS may coordinate a finite sequence of execution attempts while preserving the M7 authority boundary for every individual action.

```text
M7-authorized ExecutionPreparation #1
        ↓
M8 lifecycle + execution
        ↓
Observation #1
        ↓
Bounded step provider
        ↓
M7-authorized ExecutionPreparation #2
        ↓
M8 lifecycle + execution
        ↓
Observation #2
        ↓
...
```

## Core design

`ControlledAgency` owns sequencing, observation accumulation, context integration, identity uniqueness, and the hard step bound.

It does not own:

- proposal creation;
- validation;
- policy decisions;
- confirmation decisions;
- authorization;
- authorization integrity;
- capability selection;
- plugin invocation;
- credentials;
- recovery policy.

The next-step provider is therefore not an authority source. It may only return an already-formed `ExecutionPreparation`, and that preparation must be `READY` before it reaches the M8 execution runtime.

## Responsibilities

- require a valid initial `ExecutionPreparation`;
- require each subsequent step to remain inside the `ExecutionPreparation` contract;
- enforce a positive hard `max_steps` bound;
- preserve distinct `execution_id` values per step;
- execute steps serially through the existing M8.1 runtime;
- create one lifecycle record per executed step using M8.4 semantics;
- integrate each observation through M8.3;
- expose an immutable run result;
- stop deterministically on blocked/invalid preparations, duplicate identities, provider errors, execution failure without a next-step provider, or step-limit exhaustion.

## Semantic walls

```text
Multi-Step Agency ≠ Multi-Step Authorization
Sequencing ≠ Authority
Observation ≠ Permission for the next action
Failure ≠ Implicit Retry
Step Provider ≠ Policy Engine
Step Provider ≠ Authorization Engine
```

Every distinct action still requires its own M7 authority chain and resulting `ExecutionPreparation`.

## Explicit non-goals

M8.5 does not implement unrestricted autonomous planning, hidden retries, recovery strategy, workers, dynamic plugin loading, policy, confirmation, or authorization.

Those concerns remain in their existing authority boundaries or later M8.6/M9 work.

## Verification

Focused and full-suite verification are pending from the user's real checkout.
