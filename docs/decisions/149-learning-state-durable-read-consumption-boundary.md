# Decision 149 — Learning-State Durable Read Consumption Boundary

## Status
IMPLEMENTED / VERIFIED LOCALLY

## Parent
`79524b8877efd2f6179e3b8623dc03b7f327b98a` — M23.136 Learning-State Consumption Request (focused 36/36 passed).

## Purpose
M23.137 establishes the first actual durable-state read boundary after an explicit `REQUESTED` consumption request.

The mechanism accepts exactly one canonical `LearningStateExecutionLearningStateConsumptionRequest` artifact with `REQUESTED` status and performs a bounded read against caller-supplied durable-state data. It emits immutable evidence of what was read, under which request and scope, while preserving upstream provenance. The read is observational only: it never mutates or persists durable state, executes work, authorizes anything, retries, interprets meaning, or learns.

## Contract
- Accepts exactly one canonical `LearningStateExecutionLearningStateConsumptionRequest` artifact.
- Requires the source consumption request status to be `REQUESTED`; rejected requests fail closed without reading durable state.
- Requires the request's own lineage to agree with its consumption-request and validation identities.
- Requires a distinct read identity and explicit reader/purpose metadata.
- Requires supplied durable-state data to be a mapping and the requested state key to be present.
- Performs only the bounded read described by the request scope; when `fields` are supplied, only those named fields are returned from the selected state mapping.
- Rejects malformed or out-of-scope field requests without reading or repairing durable state.
- Produces immutable read/consumption evidence containing the bounded payload and a SHA-256 read fingerprint.
- Preserves the consumption-request identity, upstream provenance, scope, and rationale.
- Does not mutate the supplied durable-state object.
- Does not persist the read result or durable state.
- Does not interpret the returned data or establish truth, correctness, certainty, or usefulness.
- Does not authorize learning, execution, retry, repair, scheduling, planning, or any other downstream action.

## Boundary Ordering
Request admissibility is evaluated completely before durable-state access. A request that is not `REQUESTED`, has invalid lineage, invalid identity/scope metadata, or otherwise fails the pre-read admission boundary must fail closed without even a membership/read access against the durable-state mapping.

## Authority Walls
`Durable-State Read Consumption ≠ Durable-State Mutation`
`Durable-State Read Consumption ≠ Persistence`
`Durable-State Read Consumption ≠ Learning`
`Durable-State Read Consumption ≠ Interpretation`
`Durable-State Read Consumption ≠ Execution`
`Durable-State Read Consumption ≠ Authorization`
`Read ≠ Truth`
`Read ≠ Correctness`
`Read ≠ Certainty`
`Read ≠ Interpretation`
`Read ≠ Usefulness`
`READ ≠ Validated`
`READ ≠ Applied`
`READ ≠ Persisted`
`READ ≠ Executed`

M23.137 is deliberately the first read boundary: the system may now observe supplied durable-state data, but observation itself grants no authority to change, trust, interpret, learn from, or execute on that data.

## Architecture
`Outcome → Feedback → Evaluation → Learning Signal → Learning Signal Integrity → Learning Eligibility → Learning Proposal → Learning Proposal Decision → Proposal Application → Application Integrity → Learning-State Evidence → Learning-State Transition → Transition Integrity → Learning-State Validation → Consumption Request → Durable-State Read Consumption → Consumption Read Validation → Interpretation Request → Learning-State Interpretation → Interpretation Validation → Interpretation Validation Integrity → Semantic Use Request → Semantic Use → Semantic Use Validation → Semantic Use Integrity → Semantic Use Handoff → Semantic Use Receipt → Semantic Use Consumption → Downstream Semantic Handling → Execution Eligibility → Execution Admission / Authorization → Execution Attempt → Execution Outcome → Execution Feedback → Evaluation`

## Verification
- M23.137 focused: **19/19 passed**
- M23.137 + M23.136 embedded regression: **37/37 passed**
- M23.135 regression: **18/18 passed**
- M23.134 regression: **16/16 passed**
- M23.133 regression: **14/14 passed**
- M23.132 regression: **14/14 passed**
- M23.131 regression: **15/15 passed**
- M23.130 regression: **10/10 passed**
- M23.129 regression: **9/9 passed**
- M23.128 regression: **10/10 passed**
- M23.127 regression: **11/11 passed**
- M23.126 regression: **15/15 passed**
- M23.125 regression: **13/13 passed**
- M23.124 regression: **12/12 passed**

The initial M23.137 focused run exposed a fail-closed ordering defect: a rejected consumption request still caused a durable-state membership access. The implementation was corrected so all request-level admission and scope/lineage checks complete before any durable-state access. The corrected focused suite then passed 19/19, with M23.136 regression included for a total of 37/37. The subsequent M23.135–M23.124 regression chain passed with the results above.

The repository-wide test suite remains outside the scope of this milestone.

No merge is implied by this decision.

## Atomicity
Exactly **1 commit / 3 intended files** from M23.136.
