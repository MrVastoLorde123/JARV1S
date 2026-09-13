# Decision 045 — Autonomous AI Reasoning Provider Boundary

Proposed V1 application/runtime boundary. The autonomous reasoning path uses the existing provider-neutral AIService through a dedicated adapter. The adapter builds a bounded AIRequest from job identity, goal, working context, and recent steps; delegates to AIService; optionally selects a registered provider; requires structured-output capability; and returns provider content for the reasoning worker to interpret. It does not execute tools, grant authority, persist jobs, or select provider-specific execution behavior.
