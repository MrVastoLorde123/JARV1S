"""Default permanent-agent profiles built from explicit JARVIS contracts."""

from __future__ import annotations

from src.agents.coding_agent_policy import DEFAULT_CODING_AGENT_POLICY
from src.agents.need_evaluator import AgentNeedPolicy
from src.agents.permanent_agent import PermanentAgentDefinition


DEFAULT_CODING_AGENT = PermanentAgentDefinition(
    agent_id="coding-agent",
    name="Coding Agent",
    role=DEFAULT_CODING_AGENT_POLICY.role,
    need_policy=AgentNeedPolicy(
        allowed_capabilities=frozenset({"read_repo", "write_repo", "run_tests"}),
        max_scope_keys=16,
    ),
    operating_rules=DEFAULT_CODING_AGENT_POLICY.required_rules,
    verification_rules=DEFAULT_CODING_AGENT_POLICY.verification_rules,
)


__all__ = ["DEFAULT_CODING_AGENT"]
