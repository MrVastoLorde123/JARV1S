# M23.425–426 — Tool authorization policy semantics and evidence

## Boundary

Authorization is the authority-bearing boundary between an execution plan and a concrete tool invocation.

```text
Capability realization
        |
        v
Execution plan
        |
        v
Concrete ToolRequest
        |
        v
Static authorization policy
        |
        v
ToolExecutionAuthorization
        |
        +----> ToolAuthorizationEvidence
        |
        v
Required confirmation (when applicable)
        |
        v
Policy-neutral ToolPlanStepHandler
        |
        v
ToolService / invoker
```

## Policy semantics

A `ToolAuthorizationPolicyRule` binds a policy identifier to one request scope. A concrete request supplies `scope` and `capability_class` through its immutable metadata snapshot.

Rules evaluate in this order:

1. Scope must match. If no rule matches, authorization is denied.
2. A missing capability class is denied.
3. Explicitly denied capability classes are denied.
4. Explicitly denied tools are denied.
5. Allowed capability classes and allowed tools are checked. An empty allow list means that dimension is unrestricted within the matching rule.
6. An authorized decision is bound to the exact `PlanStep` and `ToolRequest` supplied to the policy.

Explicit deny therefore has precedence over an allow entry in the same rule.

## Evidence

`ToolAuthorizationEvidence` is an immutable, serializable snapshot of the authorization decision. It records the step, invocation, tool, scope, capability class, authorization result, policy identifier, and reason.

The evidence artifact is deliberately not an execution result, verification claim, confirmation, or persistence mechanism. Persistence belongs behind an independent store boundary.

## Non-goals

This boundary does not:

- execute tools;
- infer or invent user intent;
- convert planning into permission;
- treat confirmation as authorization;
- assert that an authorized tool invocation succeeded;
- grant verification truth to the policy layer.
