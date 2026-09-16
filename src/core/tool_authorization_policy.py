"""Deterministic policy evaluation for concrete tool execution requests.

This module decides whether a concrete request is permitted. It does not
execute tools, confirm user intent, or claim that an execution succeeded.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization
from src.tools.models import ToolRequest


_REQUEST_SCOPE_KEY = "scope"
_CAPABILITY_CLASS_KEY = "capability_class"


def _normalize_set(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")
        normalized_value = value.strip().lower()
        if normalized_value not in normalized:
            normalized.append(normalized_value)
    return tuple(normalized)


@dataclass(frozen=True)
class ToolAuthorizationPolicyRule:
    """One immutable allow/deny policy rule.

    Deny rules take precedence over allow rules. An empty allow list means
    that dimension is unrestricted within the matching rule.
    """

    policy_id: str
    scope: str
    allowed_capability_classes: tuple[str, ...] = ()
    denied_capability_classes: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = ()
    denied_tools: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id.strip():
            raise ValueError("policy_id must be a non-empty string")
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ValueError("scope must be a non-empty string")
        object.__setattr__(self, "policy_id", self.policy_id.strip())
        object.__setattr__(self, "scope", self.scope.strip().lower())
        object.__setattr__(
            self,
            "allowed_capability_classes",
            _normalize_set(
                self.allowed_capability_classes,
                "allowed_capability_classes",
            ),
        )
        object.__setattr__(
            self,
            "denied_capability_classes",
            _normalize_set(
                self.denied_capability_classes,
                "denied_capability_classes",
            ),
        )
        object.__setattr__(
            self,
            "allowed_tools",
            _normalize_set(self.allowed_tools, "allowed_tools"),
        )
        object.__setattr__(
            self,
            "denied_tools",
            _normalize_set(self.denied_tools, "denied_tools"),
        )


class StaticToolAuthorizationPolicy:
    """Evaluate one deterministic collection of authorization rules."""

    def __init__(self, rules: tuple[ToolAuthorizationPolicyRule, ...]) -> None:
        if not isinstance(rules, tuple):
            raise TypeError("rules must be a tuple")
        if not rules:
            raise ValueError("at least one authorization rule is required")
        if any(not isinstance(rule, ToolAuthorizationPolicyRule) for rule in rules):
            raise TypeError("rules must contain only ToolAuthorizationPolicyRule values")
        policy_ids = [rule.policy_id for rule in rules]
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("policy_id values must be unique")
        self._rules = rules

    @property
    def rules(self) -> tuple[ToolAuthorizationPolicyRule, ...]:
        return self._rules

    def authorize(
        self,
        step: PlanStep,
        request: ToolRequest,
    ) -> ToolExecutionAuthorization:
        if not isinstance(step, PlanStep):
            raise TypeError("step must be a PlanStep")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        scope = request.metadata.get(_REQUEST_SCOPE_KEY)
        capability_class = request.metadata.get(_CAPABILITY_CLASS_KEY)
        normalized_tool = request.tool_name.strip().lower()
        normalized_scope = scope.strip().lower() if isinstance(scope, str) else None
        normalized_class = (
            capability_class.strip().lower()
            if isinstance(capability_class, str)
            else None
        )

        for rule in self._rules:
            if normalized_scope != rule.scope:
                continue

            if normalized_class is None:
                return ToolExecutionAuthorization(
                    step_id=step.step_id,
                    request=request,
                    authorized=False,
                    policy_id=rule.policy_id,
                    reason="request is missing a non-empty capability_class",
                )

            if normalized_class in rule.denied_capability_classes:
                return ToolExecutionAuthorization(
                    step_id=step.step_id,
                    request=request,
                    authorized=False,
                    policy_id=rule.policy_id,
                    reason=f"capability class '{normalized_class}' is denied",
                )

            if normalized_tool in rule.denied_tools:
                return ToolExecutionAuthorization(
                    step_id=step.step_id,
                    request=request,
                    authorized=False,
                    policy_id=rule.policy_id,
                    reason=f"tool '{normalized_tool}' is denied",
                )

            class_allowed = (
                not rule.allowed_capability_classes
                or normalized_class in rule.allowed_capability_classes
            )
            tool_allowed = not rule.allowed_tools or normalized_tool in rule.allowed_tools
            authorized = class_allowed and tool_allowed

            if authorized:
                reason = "request matches policy allow rules"
            elif not class_allowed:
                reason = f"capability class '{normalized_class}' is not allowed"
            else:
                reason = f"tool '{normalized_tool}' is not allowed"

            return ToolExecutionAuthorization(
                step_id=step.step_id,
                request=request,
                authorized=authorized,
                policy_id=rule.policy_id,
                reason=reason,
            )

        return ToolExecutionAuthorization(
            step_id=step.step_id,
            request=request,
            authorized=False,
            policy_id="no-matching-policy",
            reason=f"request scope '{normalized_scope}' is not authorized",
        )


@dataclass(frozen=True)
class ToolAuthorizationEvidence:
    """Serializable evidence snapshot for one authorization decision.

    This is an evidence artifact, not a persistence mechanism and not an
    execution result. The caller may persist it through an independent store.
    """

    step_id: str
    invocation_id: str | None
    tool_name: str
    scope: str
    capability_class: str
    authorized: bool
    policy_id: str
    reason: str

    def __post_init__(self) -> None:
        for field_name in ("step_id", "tool_name", "scope", "capability_class", "policy_id", "reason"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.authorized, bool):
            raise TypeError("authorized must be a bool")

    @classmethod
    def from_authorization(
        cls,
        authorization: ToolExecutionAuthorization,
    ) -> "ToolAuthorizationEvidence":
        if not isinstance(authorization, ToolExecutionAuthorization):
            raise TypeError("authorization must be a ToolExecutionAuthorization")
        metadata: Mapping[str, object] = authorization.request.metadata
        scope = metadata.get(_REQUEST_SCOPE_KEY)
        capability_class = metadata.get(_CAPABILITY_CLASS_KEY)
        if not isinstance(scope, str) or not scope.strip():
            raise ValueError("authorized request evidence requires a non-empty scope")
        if not isinstance(capability_class, str) or not capability_class.strip():
            raise ValueError(
                "authorized request evidence requires a non-empty capability_class"
            )
        return cls(
            step_id=authorization.step_id,
            invocation_id=authorization.request.invocation_id,
            tool_name=authorization.request.tool_name,
            scope=scope.strip().lower(),
            capability_class=capability_class.strip().lower(),
            authorized=authorization.authorized,
            policy_id=authorization.policy_id,
            reason=authorization.reason,
        )

    def to_record(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "step_id": self.step_id,
                "invocation_id": self.invocation_id,
                "tool_name": self.tool_name,
                "scope": self.scope,
                "capability_class": self.capability_class,
                "authorized": self.authorized,
                "policy_id": self.policy_id,
                "reason": self.reason,
            }
        )
