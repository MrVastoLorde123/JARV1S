# M16.2 — Change Impact Assessment

## Purpose

M16.2 adds a bounded, immutable assessment of the expected impact of a `SelfDevelopmentProposal`.

The assessment describes likely scope, risk magnitude, compatibility impact, rollback feasibility, and confidence. It is evidence for later validation and policy stages, not a decision that permits the change.

## Boundary

```text
SelfDevelopmentProposal
        ↓
ChangeImpactAssessment
        ↓
(existing validation / policy / authority chain)
```

The M16.2 layer does not:

- modify source code
- authorize a self-change
- approve a proposal
- issue a policy decision
- request execution
- expand authority
- authorize identity changes

## Model

`ChangeImpactAssessment` records:

- stable assessment identity
- lineage to the M16.1 proposal
- overall impact level
- affected domains
- descriptive reasons
- dependency and compatibility impact
- rollback feasibility
- confidence in the assessment
- whether authority or identity scope is implicated
- whether authority review is required
- bounded metadata

Supported impact domains include code, data, configuration, interface, dependency, runtime, authority, identity, and unknown.

## Authority protections

Authority and identity implications are represented as impact signals only.

An authority or identity impact must be explicitly surfaced in the affected domains and requires authority review, but the assessment still exposes:

```text
change_is_authorized = False
execution_requested = False
```

Serialization also explicitly preserves the same non-authoritative wall.

## Core invariants

- Impact Assessment ≠ Authorization
- Impact ≠ Prohibition
- Risk ≠ Authority
- Confidence ≠ Certainty
- Affected Scope ≠ Permission
- Predicted Impact ≠ Observed Outcome
- Self-Development ≠ Authority Expansion

## Validation

Focused tests:

```text
python -m unittest src.tests.test_change_impact
```

M16.2 is complete when the focused test suite passes and the assessment remains a purely descriptive input to later validation/policy stages.
