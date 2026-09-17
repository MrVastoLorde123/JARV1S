# Phase 3 Decision — Systems Intelligence

## Decision

Extend JARVIS's existing capability registry and discovery surface into a capability system with explicit:

- graph relationships;
- dependency closure and cycle detection;
- measurable utility;
- higher-order composition;
- capability-to-capability leverage and compounding;
- aggregate cross-model assessment.

## Why now

The repository already models capabilities as bounded declarations and can discover/select them. That surface answers what capabilities exist and which capability may match an intent, but it does not yet model the system-level question of how capabilities depend on, combine with, or increase the usefulness of one another.

Phase 3 supplies that missing systems layer without changing the authority boundary.

## Authority boundary

The systems-intelligence layer is descriptive and analytical.

It may:

- represent relationships;
- detect dependency cycles;
- calculate prerequisite readiness;
- calculate normalized utility signals;
- model higher-order compositions;
- measure confidence-discounted leverage;
- expose system-level assessments.

It may not:

- authorize a capability;
- grant permission;
- invoke a tool;
- select or call an external provider;
- create credentials;
- persist state externally;
- establish truth or certainty.

## Epistemic rule

Utility measurements and compounding links are evidence-bearing assessments, not truth claims. Hypothesized leverage remains explicitly marked and confidence-discounted.

## Value rule

Capability value and systems leverage are criteria for future decision-making. They never become authority sources.

> Build capabilities that compound. Build boundaries that do not.

## Runtime relationship

`JarvisRuntime` exposes an injected `CapabilitySystem` as an inspectable composition boundary. The runtime retains `authorizes_execution == False` and `executes_capability == False`.
