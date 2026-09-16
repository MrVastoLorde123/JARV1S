# 384–386 — AIService Provider Contract Hardening

## Decision

Strengthen the `AIService` provider boundary so registration, capability reporting, request execution, and response materialization are deterministic typed contracts.

## M23.384 — Provider Registration Integrity

`AIService.register_provider()` requires an `AIProvider`. Empty provider names are rejected, identical re-registration of the same provider is idempotent, and conflicting replacement of an occupied provider name is rejected.

## M23.385 — Capability Contract Integrity

`AIService.get_capabilities()` requires providers to return `AICapabilities`. Required capability names must be non-empty strings and must resolve to declared boolean capability fields. Unknown names are rejected rather than silently interpreted as unsupported.

## M23.386 — Provider Response Contract Integrity

`AIService.generate()` requires a non-empty string request task and requires the provider to return an `AIResponse`. Provider-directed execution remains the provider boundary; JARVIS owns validation of the provider-neutral response shape before returning it upstream.

## Safety boundary

These checks strengthen contracts only. Provider registration does not grant authority. Capability metadata does not grant permission or execution. `AIResponse` validation does not make model output truthful or authoritative. Model routing remains cognitive selection only, while confirmation, authorization, execution, and verification remain downstream boundaries.

## Verification

User-local verification should be batched with the adjacent routing-contract regression and the full core regression.
