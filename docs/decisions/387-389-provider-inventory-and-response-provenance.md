# 387–389 — Provider Inventory and Response Provenance

## Decision

Harden `AIService` around provider-observation and provider-response provenance so external provider data cannot silently violate JARVIS's provider-neutral contracts.

## M23.387 — Provider Inventory Contract

Provider model observation must return an iterable containing only non-empty string model identifiers. Invalid inventory data is rejected before it reaches the model catalog.

## M23.388 — Response Provider Provenance

A provider-generated `AIResponse` must identify the same normalized provider name selected by `AIService`. A response naming another provider is rejected rather than accepted as trusted metadata.

## M23.389 — Response Model Identity

Provider-generated responses must expose a non-empty model identifier. The service does not infer model quality or role fitness from that identifier; it only preserves structural provenance.

## Safety boundary

These checks validate provider-neutral data integrity. Observation remains observation; a model identifier does not establish capability, quality, truth, authority, or permission. Response provenance does not make generated content authoritative and does not bypass downstream verification or execution boundaries.
