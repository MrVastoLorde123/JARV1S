"""Model-assisted proposal of arguments for a selected capability."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from src.ai.models import AIRequest
from src.ai.service import AIService
from src.core.capability_invocation import CapabilityInvocationBuilder, CapabilityInvocationError
from src.core.capability_selection import CapabilityCandidate
from src.tools.models import ToolRequest


@runtime_checkable
class CapabilityArgumentPlanner(Protocol):
    """Propose a structured argument mapping without executing a tool."""

    def propose(
        self,
        intent: str,
        capability: CapabilityCandidate,
    ) -> Mapping[str, Any]:
        ...


class AIRequestArgumentPlanner:
    """Use an AI provider to propose JSON arguments for one capability.

    The model only proposes data. ``CapabilityInvocationBuilder`` remains the
    deterministic boundary that validates and materializes a ``ToolRequest``.
    """

    def __init__(
        self,
        ai_service: AIService,
        *,
        invocation_builder: CapabilityInvocationBuilder | None = None,
        provider_name: str | None = None,
    ) -> None:
        if not isinstance(ai_service, AIService):
            raise TypeError("ai_service must be an AIService")
        self._ai_service = ai_service
        self._builder = invocation_builder or CapabilityInvocationBuilder()
        self._provider_name = provider_name

    def propose(
        self,
        intent: str,
        capability: CapabilityCandidate,
    ) -> Mapping[str, Any]:
        if not isinstance(intent, str) or not intent.strip():
            raise ValueError("intent must be a non-empty string")
        if not isinstance(capability, CapabilityCandidate):
            raise TypeError("capability must be a CapabilityCandidate")

        definition = capability.capability
        prompt = self._prompt(intent, definition)
        response = self._ai_service.generate(
            AIRequest(
                task=prompt,
                context=None,
                generation_options={"temperature": 0},
                metadata={"purpose": "capability_argument_proposal"},
            ),
            provider_name=self._provider_name,
        )

        try:
            parsed = json.loads(str(response.content))
        except (TypeError, json.JSONDecodeError) as exc:
            raise CapabilityInvocationError(
                f"AI returned invalid JSON arguments for '{definition.name}'"
            ) from exc

        if not isinstance(parsed, Mapping):
            raise CapabilityInvocationError("AI argument proposal must be a JSON object")
        return dict(parsed)

    @staticmethod
    def _prompt(intent: str, definition) -> str:
        schema = json.dumps(definition.input_schema, sort_keys=True)
        return (
            "Return ONLY a JSON object of arguments for the selected capability. "
            "Do not include markdown, explanation, or the tool name. "
            f"User intent: {intent}\n"
            f"Capability: {definition.name}\n"
            f"Description: {definition.description}\n"
            f"Input schema: {schema}"
        )


class CapabilityInvocationService:
    """Compose selection output, argument proposal, and deterministic validation."""

    def __init__(
        self,
        argument_planner: CapabilityArgumentPlanner,
        *,
        invocation_builder: CapabilityInvocationBuilder | None = None,
    ) -> None:
        if not isinstance(argument_planner, CapabilityArgumentPlanner):
            raise TypeError("argument_planner must implement CapabilityArgumentPlanner")
        self._argument_planner = argument_planner
        self._builder = invocation_builder or CapabilityInvocationBuilder()

    def build_request(
        self,
        intent: str,
        capability: CapabilityCandidate,
    ) -> ToolRequest:
        arguments = self._argument_planner.propose(intent, capability)
        return self._builder.build(capability.capability, arguments)
