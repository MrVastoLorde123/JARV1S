# JARVIS Anywhere — Remote Access Architecture Concept

Status: architecture concept only. No implementation is implied.

## 1. Problem

Near-term JARVIS remains hosted on one laptop.

The user needs access from:
- the host laptop;
- a second laptop;
- a phone;
- future trusted devices.

The core decision:

Remote access should mean access to JARVIS, not accidental access to the operating system hosting JARVIS.

## 2. Current topology

    User
      |
    Human Operating Layer
      |
    JARVISRuntime
      |
    LocalProvider
      |
    llama-server
      |
    GGUF model

JARVIS already has local HTTP command/control surfaces. V2 should put a secure boundary in front of JARVIS rather than exposing internal services directly.

## 3. Target topology

    TRUSTED DEVICE
          |
    encrypted private transport
          |
    JARVIS ACCESS GATEWAY
          |
     +----+----+----+
     |         |    |
  command     jobs state
     |         |    |
     +----+----+----+
          |
     JARVISRuntime
          |
      internal JARVIS
          |
      host + tools
          |
       local model

The gateway is the remote security boundary.

## 4. Never expose directly

Do not directly expose:
- llama-server;
- SQLite;
- internal tool ports;
- raw control-plane ports;
- unrestricted shell;
- unrestricted RDP;
- internal service-to-service ports.

The remote device should know only the public JARVIS access contract.

## 5. Candidate access models

### A — VPN plus RDP

Strengths:
- simple;
- excellent for emergency host administration.

Weaknesses:
- far broader access than JARVIS needs;
- weak phone experience;
- couples JARVIS use to Windows desktop access.

Role:
administration/recovery path.

### B — Secure JARVIS gateway

Remote device -> encrypted private transport -> authenticated gateway -> JARVISRuntime.

Strengths:
- least privilege;
- natural JARVIS experience;
- mobile-friendly;
- explicit auditability.

Role:
preferred long-term daily architecture.

### C — Hybrid

Normal use -> JARVIS gateway.

Emergency machine administration -> separate VPN/RDP-style administration path.

Role:
likely strongest long-term operating model.

## 6. Device identity

A trusted device record should eventually contain:
- device_id;
- device type;
- owner;
- credential reference;
- enrollment state;
- last-seen time;
- capability scope;
- revocation state.

Ownership of the physical device is not enough; device trust should be explicit.

## 7. Authentication versus authorization

Authentication answers:
who is this?

Authorization answers:
what can this session do?

Those remain separate.

A session should carry:
device identity + user identity + session identity + requested operation.

The canonical JARVIS authorization chain still decides whether the action is allowed.

## 8. Session continuity

Remote sessions should preserve continuity without becoming permission tokens.

Useful metadata:
- session_id;
- device_id;
- connection_id;
- event cursor;
- active jobs;
- pending approvals;
- reconnect state.

Reconnect:
authenticate -> restore session -> replay missed events -> refresh current state -> continue.

Network loss must never imply retry.

## 9. Mobile model

The phone does not need the entire desktop cockpit.

Useful mobile actions:
- send request;
- inspect job;
- approve;
- view blocker;
- inspect verification;
- resume/reconcile;
- view status.

The phone should use the same JARVIS protocol as the desktop client.

## 10. Remote command contract

Potential remote commands:
- SEND_REQUEST;
- LIST_JOBS;
- INSPECT_JOB;
- RESUME_JOB;
- CANCEL_JOB;
- RECONCILE_JOB;
- APPROVE;
- GET_STATE;
- GET_EVENTS.

The remote layer transports canonical semantics rather than inventing a second authorization system.

## 11. Event continuity

Important remote events:
- job started;
- progress;
- waiting for user;
- approval required;
- tool failure;
- verification update;
- completion;
- ambiguous external effect;
- blocker.

Clients reconnect using an event cursor.

## 12. Approval security

Remote approval should be:

proposal -> approval request -> authenticated device -> exact action/context shown -> explicit user approval -> canonical authorization -> execution

A notification tap alone is not authorization.

## 13. Host isolation

The access gateway should have only the privileges it needs.

Prefer:
- local services on loopback;
- gateway with least privilege;
- model server internal;
- database internal;
- host administration separate.

## 14. Emergency path

Maintain a separate administrative recovery route for:
- host failure;
- gateway failure;
- broken deployment;
- revoked device;
- credential failure;
- stuck runtime.

Daily JARVIS access and host administration should remain separate.

## 15. Remote acceptance criteria

Before production use, demonstrate:
1. no direct exposure of internal service ports;
2. authenticated remote access;
3. device revocation;
4. reconnect continuity;
5. missed-event recovery;
6. approval through canonical authorization;
7. network loss without duplicate execution;
8. no remote privilege escalation;
9. device/session auditability;
10. independent emergency host administration.

## 16. Long-term principle

Anywhere access should make JARVIS portable, not make the host vulnerable.
