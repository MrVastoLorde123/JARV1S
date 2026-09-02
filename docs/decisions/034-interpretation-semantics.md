# Decision 034 — Interpretation Semantics

## Status

Accepted as M7.2 design.

## Context

M7.1 established a provider-neutral `ReasoningContext` that separates observed information, evidence, persisted claims, and current state. M7.2 defines what a reasoning system may conclude from that context without promoting model-derived conclusions into authoritative facts.

## Decision

Interpretation is a separate semantic output boundary:

```text
WorkingContext
    ↓
ReasoningContext
    ↓
Interpretation
    ├── derived claims
    ├── uncertainties
    ├── conflicts
    └── missing information
```

An interpretation is non-authoritative by construction. It may describe what the available inputs appear to imply, but it does not mutate memory, change execution state, authorize tools, or execute actions.

### Derived claims

A `DerivedClaim` must contain explicit support references into the originating `ReasoningContext`. Supported and conflicted claims cannot exist without support references. Confidence is descriptive only and does not grant authority.

### Uncertainty

`Uncertainty` represents unresolved ambiguity or weakness in the available information. It may reference the inputs that caused the uncertainty and may carry a severity value.

### Conflicts

`InterpretationConflict` represents incompatible or tensioning inputs. Conflict is preserved explicitly rather than forcing the reasoning system to select one input as truth.

### Missing information

`MissingInformation` identifies information that would be useful or necessary for a stronger conclusion but is unavailable in the current context. It is not itself a factual claim.

### Output-only semantics

M7.1 reserves `DERIVED` and `PROPOSED` as reasoning-output roles. M7.2 uses the `DERIVED` role for derived claims. Nothing in M7.2 authorizes a proposal or action.

## Deterministic boundary

`InterpretationValidator` validates structure only:

- interpretation request must match the reasoning request
- support references must point inside the reasoning context
- supported/conflicted claims require support
- types and ranges must be valid

Validation does not decide whether the model's conclusion is true. Truth validation remains outside this semantic layer.

## Non-goals

M7.2 does not:

- invoke an AI provider
- implement a reasoning model
- select tools
- prioritize actions
- authorize actions
- execute actions
- write memory
- replace `WorkingContext` or `ReasoningContext`

## Consequence

JARVIS can now represent the difference between:

```text
input facts/claims
    ↓
what JARVIS infers
    ↓
why it inferred it
    ↓
what remains uncertain or missing
```

without collapsing inference into truth. This establishes the foundation for later prioritization semantics.
