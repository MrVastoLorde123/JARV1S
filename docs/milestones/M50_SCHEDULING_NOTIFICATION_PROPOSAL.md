# M50 — Scheduling / Notification Proposal

Builds on the verified M49 proactive-proposal boundary.

## Included
- immutable `SchedulingNotificationProposal`
- immutable `SchedulingNotificationProposalSet`
- explicit SCHEDULE / NOTIFY / SCHEDULE_AND_NOTIFY modes
- optional timezone-aware scheduling bounds
- exact M49 proposal-set lineage
- candidate and uncertainty lineage preservation
- explicit non-truth/non-intent/non-authority/non-scheduling/non-notification/non-authorization/non-execution semantics
- focused scheduling-notification tests
- repository-local contract verifier and decision documentation
- public agency exports

## Boundary
M50 represents a possible future scheduling or notification action. It does not schedule anything, send notifications, infer user intent, request authorization, select providers/tools, or execute capabilities.
