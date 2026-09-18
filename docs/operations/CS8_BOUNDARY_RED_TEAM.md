# CS8 — Boundary Red-Team

## Boundary

CS8 is an adversarial verification stage. It assumes the deployment works and attempts to cross the authority boundaries that must remain deterministic.

The red-team target chain is:

proposal != authorization
authorization != execution
execution outcome != verification truth
verification / learning != authority
model / provider != JARVIS permission
recovery / replay metadata != semantic permission
interface / API payload != backend authority

## Attack coverage

### Proposal vs authorization

A coding proposal is staged without executing. Confirmation is one-shot. A tampered staged plan fails its fingerprint check before execution.

### Authorization vs execution

Authorization integrity is bound to the exact request. Execution preparation rejects missing authorization. Execution-attempt rejects a result whose invocation identity does not match the prepared handoff.

### Execution vs verification

A positive execution claim cannot override contradictory verification evidence. The CS8 test intentionally supplies a positive coding status with a failed verification result and requires a CONTRADICTED claim state.

### Learning vs authority

Post-execution learning persists as EPISODIC/CANDIDATE. Learning metadata explicitly remains non-authoritative and cannot establish truth, certainty, or authority.

### Model vs JARVIS

A provider is allowed to return a malicious structured response that claims authority and requests a tool call. JARVIS treats it as model output; no tool invocation is created.

Model routing remains cognitive selection only.

### Recovery vs permission

A semantic-processing failure is not retried by the integrated runtime. The failure path records ABANDON and the processor is called exactly once.

### Interface/API

The command transport accepts only the interface content as semantic input. Extra JSON fields such as authorized, authorization_granted, execute, and policy_decision do not become backend authority. The returned interface response remains explicitly non-authoritative.

## Verification

Focused red-team suites:

    python -m unittest src.core.tests.test_deployment_closure_cs8_boundary_red_team -v
    python -m unittest src.ai.tests.test_deployment_closure_cs8_model_boundary -v

Authoritative regression:

The authoritative core regression is owned by `.github/workflows/deployment-closure-verification.yml`. The CS8 red-team workflow is intentionally focused and does not duplicate the canonical regression gate.

## Acceptance criteria

CS8 is VERIFIED / CLOSED only when:

1. every focused attack passes;
2. the authoritative core regression passes in the same head;
3. historical interface and AI closure gates pass;
4. no test demonstrates a proposal, model response, recovery record, execution outcome, or learning record crossing into authority without the canonical deterministic boundary;
5. no main change or merge is performed.

CS8 adds adversarial verification coverage. It does not create a second execution path or expand runtime authority.