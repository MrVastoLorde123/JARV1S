# M22.38 — Future Adaptation Execution Feedback Decision

## Boundary
M22.38 converts one immutable M22.37 future-adaptation execution feedback evaluation into one immutable explicit decision.

## Contract
- Consume exactly one M22.37 evaluation artifact.
- Preserve exact execution/preparation/admission/proposal/decision/evaluation/feedback/source-feedback/candidate/source-candidate/source-execution/domain/policy lineage.
- Preserve the M22.37 evaluation identity separately from the historical evaluation identity carried by M22.36.
- Produce only explicit `ACCEPT`, `DEFER`, or `REJECT` decisions.
- Use a deterministic baseline provider; provider output identity is validated by the service.
- Bound confidence to `[0.0, 1.0]`.
- Recursively freeze related context and decision metadata.

## Baseline policy
- A failure signal defers because more evidence is required.
- Confidence below `0.5` defers.
- Otherwise the decision accepts the observed evaluation evidence.

## Authority wall
M22.38 is a decision boundary, not an execution-authority boundary.

A decision cannot:
- authorize execution;
- request retry;
- revoke execution;
- mutate memory;
- grant general authority.

The decision is evidence-guided planning state for the downstream boundary.

## Identity rule
The new `decision_id` is deterministic and distinct from the upstream M22.37 evaluation identity. Upstream identities remain lineage rather than being overwritten by the new artifact identity.
