# M28 — JARVIS OS prototype

## Decision
Prototype the JARVIS interface as one persistent operating environment with multiple lenses over shared machine state.

## Principles
- The backend snapshot and gateway remain the source of runtime truth.
- One React application owns navigation and selection state.
- Lenses are views of the same operation, not independent destinations with duplicated state.
- Mission, context, runtime, and ability remain connected to the same selected work object.
- Runtime pressure and attention change emphasis without inventing backend state.
- Operator actions remain bounded by existing gateway/backend authority.
- The prototype is intentionally isolated on its own feature branch so V1 remains a reference specimen.

## Prototype questions
- Does a shared-world model feel more coherent than application-like pages?
- Does a persistent causal operation make navigation easier to understand?
- Can JARVIS expose enough operational state without returning to dashboard clutter?
- Which spatial and adaptive behaviors should survive into a future interface platform or skin system?
