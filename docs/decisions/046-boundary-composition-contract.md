# M23.1 — Boundary Composition Contract

## Decision

JARVIS needs a reusable composition mechanism for existing cognitive, authority, execution, learning, and adaptation boundaries. The composition mechanism must connect already-defined contracts without becoming a new authority layer.

## Motivation

M22 established a large family of explicit boundaries. Each boundary remains intentionally separate, while M8.5 already provides bounded multi-step execution orchestration through `ControlledAgency`. What is missing is a generic mechanism for composing typed boundary stages such as:

`evaluation → decision → proposal → admission → preparation → execution → result → feedback`

The new mechanism exists to remove repeated bespoke sequencing code without collapsing boundary responsibilities.

## Contract

`BoundaryStageSpec` defines one stage with:

- a non-empty name
- an exact input type
- an exact output type
- a callable handler

`BoundaryPipeline` composes an ordered tuple of stage specifications.

Construction fails when adjacent stage types do not match exactly. Runtime execution also requires exact type identity for each stage input and output.

`BoundaryCompositionResult` records the initial type, final value, and immutable stage observations in deterministic order.

## Failure behavior

The pipeline fails closed when:

- no stages are supplied
- a stage specification is malformed
- adjacent stage types are incompatible
- the initial runtime value has the wrong exact type
- a stage returns the wrong exact type
- a stage raises an exception

Stage exceptions are wrapped as `BoundaryCompositionError` with stage identity preserved. A failed stage is never automatically retried.

## Authority wall

The composition layer:

- does not authorize execution
- does not execute capabilities by itself
- does not grant permission or authority
- does not request retries
- does not revoke authorization
- does not mutate memory
- does not skip stages
- does not infer policy approval
- does not establish truth

Individual boundary services retain responsibility for their own policy, authorization, execution, observation, feedback, and mutation rules.

## Relationship to M8.5

M8.5 `ControlledAgency` remains the bounded multi-step execution coordinator and is not replaced. M23.1 is a lower-level composition primitive that can eventually be used to assemble broader pipelines while preserving the existing agency contract.

## Future direction

M23.1 intentionally begins with synchronous deterministic composition. Async execution, concurrency, event-driven composition, branching, retries, compensation, model routing, and agent orchestration remain separate future concerns and must not be smuggled into this primitive.
