# JARVIS V2 Roadmap — Trusted Daily Agency

Status: design baseline. No implementation implied.

V1 is the frozen operational baseline. V2 is the transition from proving the organism works to making the organism materially more useful through repeated real use.

## 1. North star

JARVIS V1 can be driven.

JARVIS V2 should become indispensable because it reliably compounds the user's ability to think, work, remember, decide, and act.

The optimization target is the whole system:

best end-to-end outcome
divided by
resource cost + latency + communication overhead + failure risk + human attention

The objective is therefore system intelligence, not maximum model intelligence.

## 2. V2 system shape

    USER / REMOTE CLIENTS
             |
       JARVIS ACCESS
             |
      CONTROL PLANE
             |
    MEMORY / CONTEXT / WORLD
             |
      DECISION / TRIAGE
             |
        DECOMPOSITION
             |
           ROUTING
             |
      AGENCY COORDINATOR
       /      |       \
  specialist worker  tools
       \      |       /
          EVIDENCE
             |
       EVALUATION /
       VERIFICATION
             |
        AGGREGATION
             |
          OUTCOME
             |
      LEARNING / CALIBRATION
             |
      BETTER NEXT RUN

The model is one capability inside this fabric.

## 3. Hard V1 walls remain

Intelligence is not authority.
Learning is not authority.
Capability is not permission.
Planning is not authorization.
Proposal is not execution.
Authorization is not verification.
Execution result is not verified effect.
Observation is not truth.
Verification is not truth.
Memory is not user intent.
Confidence is not certainty.
Prediction is not permission.

V2 adds useful capability without silently weakening these walls.

## 4. Workstreams

### A — Intelligence Fabric

Engineer the model roster as a system.

Study and measure:
- general models;
- coding models;
- specialist models;
- image/scanning models;
- lightweight decision models;
- role fitness;
- latency;
- resource cost;
- confidence behavior;
- calibration.

### B — Agency Fabric

Engineer:
- decomposition;
- routing;
- specialization;
- assignment;
- communication;
- shared evidence;
- aggregation;
- bounded recursion;
- recovery;
- verification.

### C — Anywhere Access

Engineer:
- continuous host operation;
- secure private transport;
- authenticated JARVIS access;
- device identity;
- session continuity;
- phone and laptop clients;
- least privilege;
- remote observability;
- reconnect/recovery.

### D — Workflow / Knowledge Fabric

Engineer:
- procedural memory;
- playbooks;
- research workflows;
- map/reduce-style processing;
- triage;
- reusable task templates;
- learned routing;
- workflow-specific verification.

### E — Improvement Fabric

Engineer:
- outcome logging;
- calibration;
- reliability metrics;
- human correction feedback;
- model-selection feedback;
- workflow improvement;
- agency improvement.

## 5. Roadmap

### V2-0 — Real-Use Observation

First establish what actually limits JARVIS.

Capture:
- recurring real tasks;
- repeated re-explanation;
- capability gaps;
- agent failures;
- model failures;
- routing failures;
- communication overhead;
- verification gaps;
- human intervention;
- latency/resource problems;
- remote-access requirements.

Output:
real-use corpus + capability gap map + agency gap map + communication gap map + remote-access requirements.

Gate:
no large V2 implementation is justified until representative real-work evidence exists.

### V2-1 — Intelligence Fabric

Engineer the model layer as a portfolio of roles rather than one permanent model.

Roles:
GENERAL
DIAGNOSTIC
CODING
VERIFICATION
LIGHTWEIGHT
VISION / SCANNING
ROUTING / TRIAGE

Measure task fitness, resource cost, latency, reliability, structured-output quality, and calibration.

Gate:
every active role has measured fitness and known limitations.

### V2-2 — Agency Fabric

Engineer multi-agent work as a governed task graph.

Target:
goal -> decompose -> route -> assign -> parallel/sequential work -> collect -> evaluate -> aggregate -> verify -> continue/ask/complete.

Gate:
multi-agent execution must beat an equivalent simpler approach on representative tasks within a bounded resource envelope.

### V2-3 — Always-On + Anywhere

JARVIS becomes continuously available from trusted devices without exposing its internal services.

Near-term:
host laptop remains the JARVIS host.

Remote clients:
second laptop and phone.

Preferred long-term pattern:
remote client -> secure private transport -> authenticated JARVIS gateway -> canonical JARVISRuntime.

RDP remains an administration path, not the primary JARVIS interface.

Gate:
no direct public exposure of model, database, internal tool, or unrestricted host-control ports.

### V2-4 — Workflow + Knowledge Fabric

Turn recurring work into reusable, inspectable workflows.

Target:
incoming work -> triage -> context retrieval -> parallel investigation -> synthesis -> verification -> reusable lesson.

Gate:
repeated work measurably requires less human intervention and less re-explanation.

### V2-5 — Learning + Calibration Fabric

Measure:
- routing accuracy;
- calibration;
- escalation quality;
- task completion;
- verified success;
- false-success rate;
- human correction;
- repeated failure;
- latency;
- resource use;
- communication volume.

Target:
execution trace -> outcome -> evaluation -> improvement candidate -> validation -> accepted change -> better future routing/workflow.

Gate:
measurable improvement without authority expansion.

### V2-6 — Trusted Daily Agency

The V2 demonstration is a real recurring task where JARVIS:
- reconstructs context;
- chooses capabilities/models;
- decomposes work;
- coordinates workers;
- survives interruption;
- obtains human approval only when needed;
- distinguishes executed/observed/verified;
- learns from the result;
- performs the next occurrence better.

That is the actual V2 completion criterion.

## 6. Agency communication principle

The goal is not maximum communication.

It is maximum useful information transfer per unit of cost.

Every agent handoff should answer:
- what is the task;
- what is in scope;
- what is known;
- what evidence exists;
- what was attempted;
- what happened;
- what is uncertain;
- what is blocked;
- what should happen next;
- how the result can be verified.

Full traces remain available for audit. Normal handoffs carry minimum sufficient context.

## 7. Bounded recursion

Recursive delegation is a tool, not a default.

Each child task requires:
- bounded scope;
- bounded depth;
- explicit budget;
- parent identity;
- completion condition;
- provenance;
- merge path.

Never permit unbounded agent spawning.

## 8. V2 dependency graph

    V1 FREEZE
       |
       +--> REAL USE CORPUS
       |        |
       |        +--> CAPABILITY GAPS
       |        +--> AGENCY GAPS
       |        +--> COMMUNICATION GAPS
       |
       +--> MODEL EVALUATION
       |        |
       |        +--> ROUTING POLICY
       |
       +--> EXTERNAL SYSTEM STUDY
       |        |
       |        +--> MECHANISM CARDS
       |
       +--> REMOTE ACCESS CONCEPT
                |
                +--> SECURE TOPOLOGY
                         |
                         +--> AGENCY FABRIC
                                  |
                                  +--> WORKFLOW / KNOWLEDGE
                                           |
                                           +--> LEARNING / CALIBRATION
                                                    |
                                                    +--> TRUSTED DAILY AGENCY

## 9. V2 rule

Do not ask: what milestone number comes next?

Ask: what currently limits JARVIS from being the most useful reliable partner it can be with the resources we actually have?

Then engineer the smallest complete causal seam that solves that limitation.

USE -> OBSERVE -> IMPROVE -> USE BETTER
