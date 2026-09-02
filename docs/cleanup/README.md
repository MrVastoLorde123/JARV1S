# Repository Cleanup Notes

M7 cleanup preserves implementation history and separates historical checkpoints from future development.

## Canonical M7 Branches

```text
feature/m7-1-reasoning-input-semantics
feature/m7-2-interpretation-semantics
feature/m7-3-prioritization-semantics
feature/m7-4-proposed-consequences
feature/m7-5-consequence-validation
feature/m7-6-policy-input-semantics
feature/m7-7-1-validation-identity-repair
feature/m7-7-policy-evaluation
feature/m7-8-confirmation-semantics
feature/m7-8-1-confirmation-integrity
feature/m7-9-authorization-semantics
feature/m7-9-1-authorization-integrity
feature/m7-10-execution-semantics
```

## Closeout Branch

`milestone/m7-complete` is the documentation-complete M7 baseline.

## Disposable Branches

M7 experimentation produced additional suffixed branch variants. They are not architectural milestones. They should be removed after verifying that no unique work remains outside the canonical branches.

## Rule

Do not rewrite or squash milestone semantics merely for visual cleanliness. Historical ADRs and checkpoint branches are part of the design record.
