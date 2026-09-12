# 014 — M29 Coding Claim / Evidence Integration

## Status

Proposed implementation boundary for M29 integration.

## Purpose

Connect the bounded M28 coding worker result to the M29 deterministic claim/evidence evaluator without changing tool authority or introducing peer review, dispute workflows, human escalation, or resource governance.

## Boundary

```text
M28 coding result
      ↓
claim + evidence construction
      ↓
M29 evaluator
      ↓
VERIFIED / CONTRADICTED / UNKNOWN / SUPPORTED
      ↓
structured result
```

The worker remains responsible for bounded execution through the existing tool gate. The integration layer only translates the resulting observations into M29 records and evaluates them.

## Worker observation preservation

The M28 `CodingAgentResult` now preserves the `ToolResult` from every attempted `write_file` operation in `edit_results`.

This is required because a claim/evidence boundary must retain provenance for independently produced observations rather than reconstructing tool outcomes from a final status string.

The integration boundary rejects inconsistent worker results when `edit_results` does not match `edits_attempted`.

## Claim construction

A coding execution produces one M29 `Claim` with:

- the coding task ID
- actor `coding_agent`
- the requested objective
- worker outcome status/counts/message
- operation ID when supplied
- plan rationale and verification contract provenance

The claim is created in `PROPOSED` state. The worker cannot assign `VERIFIED` to it.

## Evidence construction

Each successful `write_file` observation becomes `FILESYSTEM_OBSERVATION` evidence containing the observed tool result, target path, invocation ID, edit index, task ID, and coding operation provenance.

A failed `write_file` becomes explicit `CONTRADICTION` evidence because the attempted operation did not establish the claimed successful implementation.

The bounded `run_test` result becomes `TEST_RESULT` or `BUILD_RESULT` evidence according to the verification runner. Its `passed` field is derived from the actual `ToolResult.success` value, not from the agent's status string.

## Evaluation

The existing M29 evaluator remains authoritative for state derivation:

- no evidence → `UNKNOWN`
- independent observation → `SUPPORTED`
- passing build/test → `VERIFIED`
- failed build/test or contradiction → `CONTRADICTED`
- contradiction takes precedence over support

The integration adapter does not alter those rules.

## Service seam

`CodingAgentService.execute_and_evaluate()` executes the exact supplied M28 plan through the existing worker boundary and then passes the structured result to the M29 adapter.

This creates a concrete end-to-end software seam without granting the evaluator any execution authority.

## Invariants

The M29 integration must not:

- invoke tools itself
- bypass confirmation or policy
- mutate tool authority
- convert agent output directly into `VERIFIED`
- infer verification success from worker status alone
- discard task or operation provenance
- introduce peer agents or dispute workflows
- introduce computational resource scheduling

## Future boundary

Later work may consume the structured M29 evaluation for broader governance. Those capabilities remain outside this milestone.
