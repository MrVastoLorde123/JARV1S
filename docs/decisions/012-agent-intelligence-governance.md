# 012 — Agent Intelligence Governance

## Status

Accepted architectural direction.

## Context

JARVIS is not itself the AI. JARVIS is the deterministic operating and governance layer around AI capabilities. LLM agents provide reasoning, interpretation, planning, domain expertise, and judgment where those capabilities cannot be reliably encoded as deterministic rules.

JARVIS must therefore not attempt to be smarter than its agents or to independently decide whether an agent's claim is true. Instead, JARVIS controls how intelligence is allowed to behave, what evidence is required before accepting a claim, what consequences are permitted while uncertainty remains, and when uncertainty must be escalated to the human operator.

The M28 coding-agent failure where an LLM proposed `public/index.html` even though the repository uses `ui/index.html` demonstrates why agents require JARVIS-owned environment knowledge and bounded context composition before planning.

## Core principle

> JARVIS does not need to know whether an agent's answer is correct. JARVIS needs to know what evidence would be required before accepting that answer as correct.

The system must never treat an LLM claim as truth merely because an agent produced it.

> No claim becomes accepted merely because an agent said it.

## Intelligence separation

### JARVIS owns deterministic governance

JARVIS owns and controls:

- environment and repository knowledge
- tool authority and permissions
- agent contracts and boundaries
- task routing and composition
- skill selection
- state and provenance
- evidence collection
- verification requirements
- policy and confirmation
- conflict and uncertainty handling
- human escalation
- future resource governance

### Agents own non-deterministic intelligence

Agents may provide:

- interpretation
- domain reasoning
- planning
- pattern recognition
- implementation proposals
- professional judgment
- diagnosis and hypothesis generation

Agent intelligence is advisory until supported by the evidence and authority pipeline.

## Agent organization

JARVIS will use two complementary structures.

### Organizational hierarchy

```text
JARVIS
  ↓
Permanent Domain Agent
  ↓
Temporary Task Agent / Worker
```

Permanent agents are appointed domain managers. They have explicit identities, responsibilities, rules, skills, boundaries, and knowledge requirements.

Temporary agents are task-scoped instances operating under the doctrine of their permanent domain agent. They do not gain independent system authority.

Unlimited recursive sub-agent spawning is intentionally avoided. Permanent agents may request peer review from other permanent agents rather than creating arbitrary trust hierarchies.

### Verification network

```text
Permanent Agent A  ↔  Permanent Agent B
        ↕                    ↕
   reviewer / specialist / verifier
```

Permanent agents may collaborate as peers. Peer relationships exist to generate independent reasoning and challenge conclusions, not to create additional authority.

A peer does not become trusted merely because it is another agent. Its output is another claim and possible source of evidence.

## Permanent agent doctrine

Permanent agents receive professional doctrine from JARVIS, including:

- domain rules
- permanent skills
- dynamic skills relevant to the current situation
- domain-specific boundaries
- required evidence standards
- verification expectations
- allowed peer relationships
- operating constraints

A representative coding-agent doctrine may include:

- never modify outside the authorized workspace
- never invent repository paths
- inspect the environment before editing
- follow existing project conventions
- use bounded verification
- never bypass confirmation
- prefer the smallest valid change

## JARVIS-owned knowledge and context composition

JARVIS houses the repository of reusable knowledge used to compose agent context.

Knowledge is separated into reusable classes such as:

```text
JARVIS Knowledge
├── environment knowledge
├── repository knowledge
├── verification knowledge
├── operating constraints
├── agent rules
└── skill repository
```

Skills are not assumed to be static. JARVIS selects and composes the relevant skills for the current situation and passes only the needed context to the appointed permanent agent.

A task-scoped context package may include:

```text
OBJECTIVE
CURRENT ENVIRONMENT
RELEVANT FILES
RELEVANT REPOSITORY FACTS
RELEVANT SKILLS
CURRENT CONSTRAINTS
REQUIRED VERIFICATION
KNOWN EVIDENCE
```

The purpose is to prevent the model from guessing facts that JARVIS can observe deterministically.

For example, before asking a coding agent to modify a frontend, JARVIS should be able to establish facts such as:

```text
Frontend root = ui/
Entry = ui/index.html
Build = npm run build
```

An agent may still be wrong, but it should not be forced to guess basic environment facts that the system can observe.

## Claim vs. Evidence

JARVIS must distinguish claims from evidence.

An agent output is a claim:

```text
Agent:
"I think this implementation is correct."
```

JARVIS records the claim and its provenance but does not automatically accept it as truth.

Evidence is produced independently through deterministic or independently inspectable mechanisms, such as:

- actual tool invocation results
- filesystem state
- exact changed content
- repository observations
- test results
- build results
- policy decisions
- independent agent review
- contradiction findings

The intended progression is:

```text
Agent:
"I think this is correct."

JARVIS:
"That's a proposal."

Reviewer:
"I agree based on the available context."

JARVIS:
"That's corroboration."

Tool:
"The file exists and matches the requested state."

JARVIS:
"That's evidence."

Test:
"The build passed."

JARVIS:
"The implementation can now be marked VERIFIED."
```

A claim may therefore move through explicit states such as:

```text
PROPOSED
SUPPORTED
VERIFIED
CONTRADICTED
DISPUTED
UNKNOWN
REJECTED
```

The exact state machine is a future implementation concern, but the semantic distinction is architectural and permanent.

## Disagreement and deadlock

Disagreement between agents is valuable because independent reasoning can expose mistakes that one model would otherwise continue reinforcing.

However, JARVIS must not allow disagreement to create an infinite loop.

When agents disagree, JARVIS should prefer bounded escalation:

1. request targeted evidence
2. request a bounded peer review
3. run deterministic verification where possible
4. re-evaluate the claims against the resulting evidence
5. if uncertainty remains materially unresolved, escalate to the human operator

The human operator remains the final authority when the system cannot resolve uncertainty safely.

JARVIS is a third hand and second brain, not an authority that must pretend to know everything.

## Consequence control

Uncertainty must constrain consequences.

An agent may reason freely inside its assigned task boundary, but the system determines what that reasoning can cause.

Examples:

- an unverified claim may be displayed as a proposal
- a read-only inspection may be allowed without confirmation
- a file write requires the existing tool authority and confirmation path
- destructive or high-risk actions require stronger authorization
- verified evidence may unlock later workflow steps

Agent intelligence, confidence, planning ability, or role never becomes authority by itself.

## Human escalation

JARVIS should be designed to reach out to the human operator when:

- evidence is insufficient
- independent agents remain materially in disagreement
- verification cannot establish the required property
- the requested action exceeds established authority
- a consequential decision cannot be safely bounded

This is not a system failure. Human escalation is an intentional part of the architecture.

## Future resource governance

JARVIS should eventually monitor and control the computational resources allocated to permanent agents and their work.

Relevant resources include, at minimum:

- CPU utilization
- GPU utilization and availability
- RAM usage
- model concurrency
- context size / memory pressure
- task priority
- thermal or system-health constraints where observable

Resource policy is intended to be bounded rather than maximizing utilization blindly. A future policy may permit high utilization while preserving safety margins and preventing the system from going overboard.

Resource governance is a future capability and must remain separate from the agent's reasoning authority.

## Architectural consequences

This decision establishes that future agent work should be designed around:

```text
JARVIS Knowledge
        ↓
Context Composition
        ↓
Permanent Domain Agent
        ↓
Temporary Task Agent
        ↓
Proposal / Claim
        ↓
Peer Review when useful
        ↓
JARVIS Authority + Verification
        ↓
Execution
        ↓
Deterministic Evidence
        ↓
Accepted State / Dispute / Human Escalation
```

The M28 pre-planning repository-context phase is therefore the first implementation step toward the broader JARVIS Agent Intelligence Governance architecture, rather than an isolated coding-agent convenience feature.
