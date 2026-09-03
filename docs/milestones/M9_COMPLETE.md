# M9 — Workforce / Delegation

## Status

**M9.6 VERIFIED / COMPLETE — M9.7 NEXT**

M9 extends M8 controlled agency into a bounded workforce and delegation layer.

## Roadmap

```text
M9.1  Worker Identity / Assignment Boundary       ✅
M9.2  Bounded Worker Runtime                      ✅
M9.3  Worker Context / Knowledge Boundary          ✅
M9.4  Worker Reporting / Result Integration        ✅
M9.5  Delegation / Coordination                   ✅
M9.6  Workforce Reliability / Recovery            ✅
M9.7  Driveability / Objective Continuation       → next
```

## Central invariant

```text
JARVIS may distribute work without distributing authority.
```

## Authority boundaries

```text
Worker ≠ Authority
Assignment ≠ Authorization
Capability ≠ Permission
Delegation ≠ Authority Escalation
Worker Output ≠ Truth
Recovery ≠ Authorization
Objective Continuation ≠ Authorization
```

## M9.6 verification

From the user's real checkout:

```text
python -m unittest src.agency.tests.test_workforce_recovery -v
Ran 8 tests in 0.001s
OK

python -m unittest
Ran 986 tests in 5.131s
OK
```

## M9.7 direction

M9.7 introduces bounded objective continuation so JARVIS can maintain an explicit objective across multiple bounded work cycles, inspect validated observations, and determine the next bounded action or delegation step without treating persistence or planning as authorization.
