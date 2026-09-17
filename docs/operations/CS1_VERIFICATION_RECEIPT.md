# CS1 Verification Receipt

## Focused Gate

**PASSED — 6/6**

Command:

```powershell
python -m unittest src.core.tests.test_canonical_cognitive_runtime src.core.tests.test_unified_request_runtime_canonical_cognition -v
```

Result:

```text
----------------------------------------------------------------------
Ran 6 tests in 0.004s

OK
```

Passed tests:

- `test_cognitive_result_never_grants_authority_or_execution`
- `test_composes_context_world_reasoning_planning_and_initiative`
- `test_invalid_request_fails_closed`
- `test_invalid_timestamp_fails_closed`
- `test_cognition_runs_before_core_processor_and_is_attached_as_metadata`
- `test_command_input_does_not_enter_cognitive_chain`

## Current Decision

CS1 remains open until the applicable full regression suite is executed and recorded. CS2 must not begin before that receipt.

No merge performed. `main` unchanged.
