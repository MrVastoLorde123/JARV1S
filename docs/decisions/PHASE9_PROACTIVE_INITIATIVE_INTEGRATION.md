# Phase 9 Decision — Proactive Initiative Integration

## Decision

Bridge the verified Phase 8 planning result into the existing M15 proactive initiative artifacts through one provider-neutral integration layer.

The bridge may detect opportunities/gaps/changes, form an initiative candidate from a feasible advisory plan, project planning utility into the existing initiative evaluation, create a proposal, optionally create a schedule artifact, and run the existing proposal safety check.

## Why

The repository already has bounded initiative and scheduling contracts. Rebuilding those mechanisms would duplicate semantics and create competing sources of initiative truth. Phase 9 therefore composes the existing artifacts instead of replacing them.

## Required walls

```text
Planning Selection ≠ Initiative Instruction
Initiative ≠ User Intent
Evaluation ≠ Authorization
Proposal ≠ Confirmation
Schedule Artifact ≠ Scheduler Job
Safety Check ≠ Authorization
Initiative ≠ Execution
```

Ambiguous world/reasoning state stays in REVIEW and does not produce a proactive proposal. Blocked plans become descriptive GAP detections only. A feasible advisory plan may become a proposal, but the proposal remains downstream of confirmation, policy, and authorization.

## Runtime

`JarvisRuntime` may receive `ProactiveInitiativeSystem` as an injected dependency. The runtime seam is composition-only and does not add authority, execution, persistence, truth, certainty, provider selection, or tool invocation.
