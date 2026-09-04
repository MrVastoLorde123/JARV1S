# M20.8 — End-to-End Long-Horizon Runtime

## Purpose

M20.8 composes the M20 long-horizon layers into one bounded runtime flow:

`Goal → Objective → Tasks → Dependencies → Progress → Plan → Next-Step Proposal → Persistence → Recovery`

The runtime coordinates existing semantics. It does not create a second planning model, execution model, or authority model.

## Recovery contract

A persisted snapshot may be recovered only when its identity, task relationships, dependency references, evaluation identities, schema version, and authority flags are valid.

Recovery reconstructs the same bounded state that was persisted. It must not infer missing progress, invent evidence, interpret recovered state as current user intent, or grant permission.

## Runtime contract

`LongHorizonRuntime.build()` creates a plan, captures progress evaluations, persists a snapshot, and produces a bounded next-step decision.

`LongHorizonRuntime.recover()` only deserializes and validates persisted state.

`LongHorizonRuntime.rebuild_from_recovery()` reconstructs the dependency graph and plan structure from recovered state, validates the persisted plan status, recomputes the bounded continuation decision from the persisted evaluations, and requires deterministic snapshot round-trip equality.

No runtime method authorizes or executes work.

## Authority boundaries

- Runtime Integration ≠ Authorization
- Persistence ≠ Authorization
- Recovery ≠ User Intent
- Recorded State ≠ Observed Reality
- Observed Progress ≠ Outcome Truth
- Next-Step Proposal ≠ Authorization
- Recovery ≠ Execution
- Orchestration ≠ Autonomous Agency

## Verification target

Focused M20.8 runtime tests must pass together with the existing M20.7 persistence tests and the full core regression suite.
