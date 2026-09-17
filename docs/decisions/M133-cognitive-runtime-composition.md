# M133 — Cognitive Runtime Composition

## Decision

Use a new typed `CognitiveRuntime` as the Phase 10 composition boundary. It consumes the existing world-model, reasoning, planning, and proactive-initiative contracts and returns one immutable `CognitiveRuntimeResult` containing exact stage artifacts and lineage.

## Why this boundary

Phase 9 already completed planning-to-initiative integration. Rebuilding initiative artifacts would duplicate M15/M21 machinery and create competing proposal/safety representations. The missing capability is therefore runtime composition, not another cognitive subsystem.

## Deliberate exclusions

The cognitive runtime does not:

- authorize execution
- execute capabilities
- validate policy
- request or grant confirmation
- create scheduler jobs
- send notifications
- select or invoke a model provider
- persist durable memory implicitly
- establish truth
- establish certainty

## Memory rule

Memory identifiers may travel through the cycle as lineage. The runtime does not silently recall or persist durable records. Persistent intelligence remains an explicit dependency/boundary.

## Provider rule

The model-provider boundary remains separate. Phase 10 is provider-neutral and can compose deterministic cognition without requiring a model.

## Failure behavior

World conflicts remain in the world snapshot. Reasoning conflicts remain explicit. Planning converts ambiguity into `REVIEW`, which prevents advisory plan selection. The initiative bridge therefore cannot create a proposal from an unresolved ambiguous cycle.

## Authority rule

A successful cognitive cycle means only that bounded cognitive stages completed. It is not a validation result, confirmation, authorization, execution handoff, truth claim, or certainty claim.
