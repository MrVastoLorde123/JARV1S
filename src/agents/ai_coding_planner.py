"""AI-backed planning adapter for the bounded coding-agent worker."""

from __future__ import annotations

import json
from typing import Any, Mapping

from src.ai.models import AIRequest
from src.ai.service import AIService

from .coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentTask,
    CodingAgentVerification,
)


class AICodingAgentPlanner:
    """Turn one coding task into a validated, non-executing coding plan."""

    _MAX_OUTPUT_TOKENS = 768

    def __init__(
        self,
        ai_service: AIService,
        *,
        provider_name: str | None = None,
        model: str | None = None,
    ) -> None:
        self._ai_service = ai_service
        self._provider_name = provider_name
        self._model = model

    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        if not isinstance(task, CodingAgentTask):
            raise TypeError("task must be a CodingAgentTask")

        response = self._ai_service.generate(
            AIRequest(
                task=self._build_prompt(task),
                context=None,
                model=self._model,
                generation_options={
                    "temperature": 0,
                    "max_output_tokens": self._MAX_OUTPUT_TOKENS,
                    "response_format": {"type": "json_object"},
                },
                metadata={
                    "actor": "coding_agent_planner",
                    "task_id": task.task_id,
                },
            ),
            provider_name=self._provider_name,
            required_capabilities=("structured_output",),
        )

        payload = self._parse_response(response.content)
        return self._decode_plan(payload)

    @staticmethod
    def _build_prompt(task: CodingAgentTask) -> str:
        repository_context = task.metadata.get("repository_context")
        if not isinstance(repository_context, str):
            repository_context = "No repository context was supplied. Do not invent environment facts."

        return (
            "You are the planning component of a bounded coding agent inside JARVIS.\n"
            "Produce ONLY one JSON object matching this shape:\n"
            "{\n"
            "  \"rationale\": \"string\",\n"
            "  \"edits\": [\n"
            "    {\"path\": \"relative/path\", \"content\": \"full UTF-8 file content\", "
            "\"overwrite\": true, \"create_parents\": false}\n"
            "  ],\n"
            "  \"verification\": {\n"
            "    \"runner\": \"python_unittest\" | \"npm_build\",\n"
            "    \"arguments\": [\"...\"],\n"
            "    \"timeout_seconds\": 120\n"
            "  }\n"
            "}\n\n"
            "Constraints:\n"
            "- Never propose shell commands.\n"
            "- Never use a runner other than python_unittest or npm_build.\n"
            "- For python_unittest, arguments may be empty; JARVIS will supply the canonical '-m unittest' prefix.\n"
            "- For npm_build, arguments must be empty; JARVIS always runs 'npm run build'.\n"
            "- File paths must be workspace-relative.\n"
            "- Only use repository paths that are supported by the observed context when possible.\n"
            "- Do not invent directories or filenames when JARVIS has provided observations.\n"
            "- An edit must contain the complete replacement file content.\n"
            "- Keep the edit set as small as practical.\n\n"
            "JARVIS OBSERVED REPOSITORY CONTEXT:\n"
            f"{repository_context}\n\n"
            f"JARVIS coding objective:\n{task.objective}"
        )

    @staticmethod
    def _parse_response(content: Any) -> Mapping[str, Any]:
        if isinstance(content, Mapping):
            payload = content
        elif isinstance(content, str):
            try:
                payload = json.loads(content)
            except json.JSONDecodeError as exc:
                raise ValueError("coding planner returned invalid JSON") from exc
        else:
            raise TypeError("coding planner response must be a mapping or JSON string")

        if not isinstance(payload, Mapping):
            raise TypeError("coding planner response root must be an object")
        return payload

    @staticmethod
    def _decode_plan(payload: Mapping[str, Any]) -> CodingAgentPlan:
        raw_edits = payload.get("edits", [])
        if not isinstance(raw_edits, list):
            raise TypeError("coding planner 'edits' must be an array")

        edits = []
        for raw_edit in raw_edits:
            if not isinstance(raw_edit, Mapping):
                raise TypeError("each coding planner edit must be an object")
            edits.append(
                CodingAgentEdit(
                    path=raw_edit.get("path"),
                    content=raw_edit.get("content"),
                    overwrite=raw_edit.get("overwrite", False),
                    create_parents=raw_edit.get("create_parents", False),
                )
            )

        raw_verification = payload.get("verification")
        if not isinstance(raw_verification, Mapping):
            raise TypeError("coding planner 'verification' must be an object")

        runner = raw_verification.get("runner")
        arguments = raw_verification.get("arguments", [])
        if not isinstance(arguments, list):
            raise TypeError("coding planner verification 'arguments' must be an array")
        if any(not isinstance(item, str) for item in arguments):
            raise TypeError("coding planner verification arguments must be strings")

        if runner == "python_unittest":
            if not arguments:
                arguments = ["-m", "unittest"]
            elif len(arguments) < 2 or arguments[:2] != ["-m", "unittest"]:
                raise ValueError(
                    "python_unittest verification arguments must begin with '-m', 'unittest'"
                )
        elif runner == "npm_build":
            if arguments:
                raise ValueError("npm_build verification does not accept arguments")

        timeout_seconds = raw_verification.get("timeout_seconds")
        if timeout_seconds is not None and not isinstance(timeout_seconds, int):
            raise TypeError("coding planner verification 'timeout_seconds' must be an integer")

        return CodingAgentPlan(
            edits=tuple(edits),
            verification=CodingAgentVerification(
                runner=runner,
                arguments=tuple(arguments),
                timeout_seconds=timeout_seconds,
            ),
            rationale=payload.get("rationale", ""),
        )


__all__ = ["AICodingAgentPlanner"]
