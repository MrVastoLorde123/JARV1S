# JARVIS External-System Study — Mechanism Extraction

Status: research only. This document does not authorize implementation.

Rule:
Do not copy an architecture wholesale.
Study the mechanism, identify the problem it solves, map it to JARVIS, test the value, then keep/adapt/reject it.

## 1. JEV / System One

Public descriptions present Jev as a typed decision model rather than a prose generator. It returns choices, scores, or yes/no probabilities and emphasizes calibrated probabilities. The public architecture is not disclosed, so internals should not be inferred. [1][2]

### Mechanism A — separate decision from generation

Many agent tasks are decisions, not writing.

Pattern:
JARVIS state -> typed decision -> selected option -> generative model only when needed.

Potential uses:
- tool selection;
- model routing;
- worker selection;
- escalation;
- task classification;
- risk category;
- workflow selection.

Status: study / high-value hypothesis.

### Mechanism B — confidence-gated escalation

Pattern:
high confidence -> cheaper path;
medium -> smaller or mid-tier reasoning;
low/tie -> stronger reasoning or human.

JARVIS should treat confidence as measured system output, not truth.

Status: study / high-value hypothesis.

### Mechanism C — calibration

Calibration asks whether predicted probability matches observed frequency over the relevant population.

JARVIS should log:
prediction + confidence + eventual outcome.

Potential uses:
- routing;
- triage;
- escalation;
- anomaly detection.

Status: study / important.

### Mechanism D — multiple cheap questions over one state

Jev documents parallel typed questions over the same state.

JARVIS analogue:
- is this coding?
- is risk high?
- is context sufficient?
- is human approval needed?
- which capability family fits?

Status: study.

### Mechanism E — cheap semantic checks

Jev documents small semantic yes/no checks around outputs.

JARVIS analogue:
draft -> cheap checks -> continue or revise/escalate.

This is not a replacement for JARVIS external-effect verification.

Status: study.

## 2. PRAXIST

Praxist is an autonomous research control plane for measurable research. It coordinates parallel peers, evaluators, evidence retention, and generation-to-generation synthesis. Its architecture separates reusable core infrastructure from task-specific projects. [3][4]

### Mechanism A — persistent research loop

generation -> parallel peers -> artifacts -> evaluation -> findings -> synthesis -> next agenda -> next generation

JARVIS analogue:
goal -> investigation generation -> parallel work -> evidence -> synthesis -> next agenda.

Status: study / high-value.

### Mechanism B — lineage DAG

PRAXIST connects artifacts, findings, decisions, agendas, and frontier state into inspectable lineage.

JARVIS analogue:
goal -> assignment -> artifact -> finding -> decision -> next assignment.

This can answer:
why did JARVIS believe this?
which work produced this?
which decision depended on it?

Status: study / very high-value.

### Mechanism C — canonical state versus derived views

PRAXIST explicitly separates canonical state, validation signals, derived views, audit snapshots, and partial output. [4]

This aligns strongly with JARVIS epistemic boundaries.

Status: study / very high-value.

### Mechanism D — context layering and audit snapshots

PRAXIST separates stable, semi-static, and dynamic prompt/context blocks and preserves rendered context for replay. [4]

JARVIS analogue:
stable instructions + role contract + task context + current state + dynamic evidence.

This directly relates to the V2 question:
what information does JARVIS need to transmit to another agent at the minimum useful granularity?

Status: study / high-value.

### Mechanism E — preserve useful partial work

PRAXIST favors retaining useful output while labeling uncertainty and continuing when safe. [4]

JARVIS analogue:
partial evidence -> preserve -> classify -> continue safely.

Status: study / high-value.

## 3. Recursive self-improvement research

Recent research formalizes an agent system as a coupled state involving:
- foundation model;
- agent harness;
- agent data system;
- trainer;
- improvement mechanism.

A general improvement loop is:
diagnose -> propose -> evaluate -> integrate. [5]

JARVIS extraction:

Do not read this as unrestricted self-modification.

Instead ask:
which component is currently limiting performance?

Possible bottlenecks:
- model;
- context;
- routing;
- decomposition;
- communication;
- tool;
- verifier;
- workflow;
- memory;
- evaluation.

Status: study / core V2 research model.

## 4. Recursive Agent Optimization

Recent work models recursive delegation as a structured execution tree in which a policy can spawn and coordinate sub-agents. [6]

JARVIS extraction:
complex task -> bounded recursive decomposition -> child results -> parent synthesis.

The transferable mechanism is structured delegation, not unlimited agent spawning.

Status: study / possible V2 mechanism.

## 5. MapReduce

Google's MapReduce separates a map function that produces intermediate keyed results from a reduce function that merges values by key. The runtime handles partitioning, scheduling, communication, and failures. [7]

JARVIS extraction:

MAP:
split a corpus/problem into bounded pieces.

GROUP:
organize findings by topic, entity, source, hypothesis, or dependency.

REDUCE:
merge into a structured synthesis.

Potential uses:
- documentation;
- logs;
- tickets;
- device inventories;
- large troubleshooting corpora.

Status: study / high-value workflow pattern.

## 6. Ticket triage

Ticket triage is a bounded routing problem:
normalize -> classify -> prioritize -> route -> escalate uncertainty.

Jev's current support-ticket example uses typed queue selection plus severity scoring with confidence-gated routing. [8]

General triage systems similarly send uncertain cases to human/manual handling rather than guessing through. [9]

JARVIS extraction:
incoming work -> normalize -> cheap classification -> priority/risk -> route -> expensive reasoning only when needed.

Status: study / high-value.

## 7. Decomposition / routing / specialization / aggregation

Treat these as four distinct agency mechanisms.

DECOMPOSITION:
turn one objective into bounded subproblems.

ROUTING:
choose the worker/model/capability.

SPECIALIZATION:
provide each worker the narrow context and contract needed.

AGGREGATION:
merge outputs while preserving provenance and disagreement.

Combined:
DECOMPOSE -> ROUTE -> SPECIALIZE -> EXECUTE -> AGGREGATE -> VERIFY

Status: study / central V2 agency model.

## 8. Synthesis across the systems

JEV contributes:
DECIDE CHEAPLY.

PRAXIST contributes:
RETAIN LINEAGE AND RESEARCH STATE.

Recursive-agent research contributes:
DECOMPOSE AND DELEGATE.

MapReduce contributes:
PARALLELIZE AND REDUCE.

Ticket triage contributes:
ROUTE BEFORE EXPENSIVE WORK.

Calibration contributes:
KNOW WHEN A DECISION IS TRUSTWORTHY ENOUGH FOR ITS INTENDED USE.

Combined JARVIS concept:

JARVIS
 -> triage
 -> decision layer
 -> decomposition
 -> routing
 -> specialist work
 -> evidence
 -> aggregation
 -> verification
 -> lineage update
 -> learning/calibration
 -> improved next run

## 9. What not to copy

JEV:
do not assume a returned probability is calibrated without measuring it.

PRAXIST:
do not turn every task into a generational research campaign.

Recursive agents:
do not permit unbounded recursion.

MapReduce:
do not parallelize dependent work.

Triage:
do not force uncertain classifications.

All external systems:
do not weaken JARVIS authority, evidence, provenance, or verification boundaries.

## 10. Pre-implementation experiments

E1 Routing economy:
one model vs static routing vs cheap triage plus escalation.

E2 Communication compression:
full transcript vs summary vs structured handoff.

E3 Parallel decomposition:
single agent vs 2-way vs 4-way decomposition.

E4 Map/reduce research:
serial versus parallel chunk research plus synthesis.

E5 Calibration:
predicted probability versus observed outcome.

E6 Lineage:
flat logs versus explicit evidence lineage.

No mechanism graduates into implementation without measurable value.

## 11. Study rule

problem exists in JARVIS
 -> mechanism plausibly solves it
 -> experiment shows measurable benefit
 -> V1 boundaries remain intact
 -> smallest implementation seam is defined

Until then the mechanism remains RESEARCH, not ROADMAP.

## Sources

[1] https://jev-agent.com/
[2] https://systemonemodels.org/guides/jev-architecture/
[3] https://github.com/sapientinc/PRAXIST
[4] https://sapientinc.github.io/PRAXIST/
[5] https://self-improving-agent.com/
[6] https://apga.github.io/RAO/
[7] https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/
[8] https://jev-agent.com/use-cases/support-ticket-triage
[9] https://carbonfay.ru/en/agents/triage-agent/

## Current conclusion

The V2 frontier is system intelligence:

not only "can the model reason?"

but:
which model should reason,
what context does it need,
how should work be decomposed,
which agent should receive it,
how should agents communicate,
how should evidence be retained,
how should results be merged,
when should uncertainty escalate,
and how should the whole system become better next time?
