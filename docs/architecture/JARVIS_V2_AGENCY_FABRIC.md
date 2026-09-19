# JARVIS V2 Agency Fabric — Engineering Concept

Status: architecture concept only. No implementation is implied.

## 1. Problem

V1 proves that a canonical JARVIS runtime can drive bounded work.

V2 must answer a harder question:

How should multiple bounded models, specialist agents, tools, and workers cooperate so the whole system is better than a single model?

The answer is a governed agency fabric.

## 2. Target topology

    JARVIS GOAL
          |
     DECISION LAYER
          |
     +----+----+
     |         |
   TRIAGE   DECOMPOSE
     |         |
     +----+----+
          |
      TASK GRAPH
          |
   +------+------+ 
   |             |
SPECIALIST     TOOL WORK
   |             |
   +------+------+ 
          |
      EVIDENCE
          |
     EVALUATION
          |
     AGGREGATION
          |
      VERIFICATION
          |
      NEXT STEP

## 3. Agent classes

Keep the initial vocabulary small.

Coordinator:
owns the task graph and coordination lifecycle.

Triage/router:
classifies work and chooses the next destination.

Researcher:
finds and evaluates information.

Builder:
creates artifacts.

Diagnostic agent:
investigates causes and inconsistencies.

Operator:
performs registered tool/capability work.

Verifier:
checks externally observable outcomes where an independent verifier exists.

Synthesizer:
combines distributed evidence into a coherent result.

A model may fill multiple roles, but the role contract stays explicit.

## 4. Assignment contract

Each assignment should carry:
- task_id;
- parent_task_id;
- assignment_id;
- objective;
- scope;
- constraints;
- allowed capabilities;
- input context;
- expected output;
- evidence requirements;
- verification requirements;
- resource budget;
- deadline/lease;
- completion criteria.

This constrains what a worker is solving.

## 5. Result contract

Each worker should return:
- assignment_id;
- status;
- result;
- evidence;
- observations;
- uncertainty;
- confidence;
- blockers;
- attempted actions;
- verification state;
- provenance;
- resource usage;
- suggested next step.

The result is machine-usable state, not just a prose response.

## 6. Communication layers

Separate:

1. STATE — lifecycle and status.
2. EVIDENCE — observations and measurements.
3. INTERPRETATION — what the evidence may mean.
4. RECOMMENDATION — proposed next step.
5. OPTIONAL REASONING — supporting detail useful for audit or diagnosis.

This prevents:

worker opinion != observation != evidence != verified outcome

## 7. Minimum sufficient handoff

The normal handoff packet should be:

Objective
Constraints
Known facts
Relevant evidence
Completed work
Open questions
Uncertainty
Blockers
Required next action
Verification state
Provenance

A full transcript remains an audit artifact, not the default context.

## 8. Task graph

Complex objectives should become explicit graphs.

Example:

    TASK
     |- research
     |- diagnosis
     |    |- network hypothesis
     |    |- protocol hypothesis
     |- implementation
     |    |- test
     '- verification

Edges represent dependencies.

This lets JARVIS know what can run in parallel, what must wait, what failed, and what evidence feeds later work.

## 9. Parallelism

Parallel work is justified when subproblems are sufficiently independent.

Benefits:
- lower wall-clock time;
- specialization;
- independent perspectives.

Costs:
- duplicated context;
- synchronization;
- resource contention;
- contradictory results;
- merge cost.

Coordinator decision:
parallelism benefit versus coordination cost.

## 10. Map / Reduce

For broad data or corpus work:

MAP:
split the corpus/problem into bounded chunks.

GROUP:
group findings by topic, entity, hypothesis, source, or dependency.

REDUCE:
merge grouped findings into a coherent result.

The point is not to copy Google's distributed implementation. The transferable lesson is to constrain the work shape so parallelism, scheduling, communication, and recovery remain manageable.

## 11. Triage

Triage should happen before expensive reasoning where possible.

    incoming work
        |
     normalize
        |
      classify
        |
   priority/risk
        |
       route
        |
   +----+----+
   |    |    |
 high med  low
   |    |    |
 specialist  small/general  stronger model/human

Uncertain work should be routed differently, not guessed through.

## 12. Specialization and routing

Routing inputs should eventually include:
- task type;
- required skills;
- required tools;
- risk;
- latency target;
- evidence target;
- available models/workers;
- recent performance;
- current capacity.

Selection should remain inside JARVIS's deterministic orchestration boundary.

## 13. Aggregation

Do not blindly concatenate outputs.

Aggregation modes:
- consensus;
- evidence union;
- conflict preservation;
- specialist weighting;
- verification-first synthesis.

Disagreement must remain visible.

## 14. Recursive delegation

Allow bounded recursive subproblems.

Each child needs:
- parent assignment;
- narrowed scope;
- explicit budget;
- bounded depth;
- completion condition;
- provenance.

The recursive tree must remain inspectable.

## 15. Failure semantics

Worker failures are classified as:
- retryable;
- replaceable;
- blocked;
- dependency-failure;
- contradictory;
- terminal.

Recovery may:
- retry;
- reroute;
- replace the worker;
- continue partial work;
- ask the user;
- terminate.

Failure handling must never create authority.

## 16. Agency budget

Track:
- max agents;
- max depth;
- max parallelism;
- max model calls;
- max tokens;
- max tool calls;
- max runtime;
- max cost;
- max retries.

Budget exhaustion is a normal state, not hidden failure.

## 17. Verification topology

For consequential outputs:

worker result
 -> observation
 -> independent evaluation/verifier
 -> verified evidence

Generation and verification should be separate whenever the outcome matters.

## 18. What JARVIS should learn about agency

Over time, JARVIS should learn:
- which tasks decompose well;
- which tasks should remain single-agent;
- which worker/model combinations work;
- what handoff summaries are sufficient;
- where workers fail;
- which evidence sources are strong;
- which thresholds are useful;
- when parallelism is worth the coordination cost;
- when escalation is cheaper than persistence.

This is agency learning. It changes future behavior, not authority.

## 19. Agency metrics

Outcome:
- useful result rate;
- verified success;
- task completion.

Efficiency:
- wall time;
- model calls;
- tokens;
- communication volume.

Coordination:
- duplicate work;
- reroutes;
- blocked time;
- merge conflicts.

Reliability:
- false success;
- unsupported claims;
- verification failures;
- repeated failures.

Human burden:
- approvals;
- clarifications;
- corrections;
- re-explanations.

A larger agent swarm that worsens these metrics is a regression.

## 20. Core principle

The goal is not to create a society of agents.

The goal is to create the smallest coordinated system that produces the best verified outcome.
