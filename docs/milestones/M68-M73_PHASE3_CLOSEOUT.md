# M68–M73 Phase 3 Closeout Map

| Checkpoint | Contract | Output |
|---|---|---|
| M68 | Capability Graph | immutable capability identities and explicit relationships |
| M69 | Capability Dependency Model | direct/transitive prerequisites, cycle detection, readiness |
| M70 | Capability Utility Model | normalized measurable usefulness dimensions and score |
| M71 | Capability Composition | ordered higher-order capability recipes and prerequisite readiness |
| M72 | Capability Compounding | confidence-discounted leverage between capabilities |
| M73 | Capability System | aggregate systems-intelligence assessment + runtime composition seam |

## Phase completion condition

The phase is complete only after the complete chain is structurally reviewed and the consolidated local gate passes:

```text
focused Phase 3 tests
        ↓
Phase 3 static contract verifier
        ↓
UI production build
        ↓
3279/3279 src.core.tests regression baseline
```

The focused suite intentionally lives outside `src/core/tests` so the long-standing core regression baseline remains stable.
