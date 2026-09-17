"""Persist production tool authorization decisions as durable evidence."""

from __future__ import annotations

from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.core.tool_authorization_policy import ToolAuthorizationEvidence
from src.tools.authorization import AuthorizationDecision
from src.tools.models import ToolDefinition, ToolRequest


class ToolAuthorizationEvidenceRecorder:
    """Record the authorization decision that precedes one tool execution."""

    def __init__(self, store: ToolAuthorizationEvidenceStore) -> None:
        if not isinstance(store, ToolAuthorizationEvidenceStore):
            raise TypeError("store must be a ToolAuthorizationEvidenceStore")
        self._store = store

    @staticmethod
    def _metadata_value(
        request: ToolRequest,
        key: str,
        default: str,
    ) -> str:
        value = request.metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
        return default

    def record(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
        decision: AuthorizationDecision,
    ):
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")
        if not isinstance(definition, ToolDefinition):
            raise TypeError("definition must be a ToolDefinition")
        if not isinstance(decision, AuthorizationDecision):
            raise TypeError("decision must be an AuthorizationDecision")

        evidence = ToolAuthorizationEvidence(
            step_id=request.invocation_id or decision.authorization_id,
            invocation_id=request.invocation_id,
            tool_name=request.tool_name,
            scope=self._metadata_value(request, "scope", "tool"),
            capability_class=self._metadata_value(
                request,
                "capability_class",
                f"risk:{definition.risk_level.value}",
            ),
            authorized=decision.authorized,
            policy_id=f"tool-gate:{decision.policy_decision.value}",
            reason=decision.reason or decision.policy_decision.value,
        )
        return self._store.save(evidence)

    def __call__(
        self,
        request: ToolRequest,
        definition: ToolDefinition,
        decision: AuthorizationDecision,
    ):
        return self.record(request, definition, decision)


__all__ = ["ToolAuthorizationEvidenceRecorder"]
