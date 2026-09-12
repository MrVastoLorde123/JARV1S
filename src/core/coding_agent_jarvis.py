"""JARVIS composition layer for explicit bounded coding tasks."""

from __future__ import annotations

from src.agents.coding_confirmation import (
    CodingAgentConfirmationService,
    coding_plan_fingerprint,
)
from src.agents.coding_service import CodingAgentService
from src.agents.coding_worker import CodingAgentTask
from src.core.jarvis import JARVIS
from src.core.models import JARVISResponse


class CodingAgentJARVIS(JARVIS):
    """Extend JARVIS with an explicit plan → confirm → execute coding route."""

    def __init__(
        self,
        *args,
        coding_agent_service: CodingAgentService | None = None,
        coding_confirmation_service: CodingAgentConfirmationService | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.coding_confirmation_service = (
            coding_confirmation_service
            if coding_confirmation_service is not None
            else CodingAgentConfirmationService()
        )

        if coding_agent_service is not None and not isinstance(coding_agent_service, CodingAgentService):
            raise TypeError("coding_agent_service must be a CodingAgentService")
        if not isinstance(
            self.coding_confirmation_service,
            CodingAgentConfirmationService,
        ):
            raise TypeError(
                "coding_confirmation_service must be a CodingAgentConfirmationService"
            )

        self.coding_agent_service = coding_agent_service

    def ask(self, query: str, provider_name: str | None = None) -> JARVISResponse:
        if not isinstance(query, str):
            raise TypeError("JARVIS query must be a string.")

        stripped = query.strip()
        if stripped.lower().startswith("code:"):
            return self._handle_coding_request(
                stripped[5:].strip(),
                provider_name=provider_name,
            )

        return super().ask(query, provider_name=provider_name)

    def _handle_coding_request(
        self,
        objective: str,
        *,
        provider_name: str | None = None,
    ) -> JARVISResponse:
        if not objective:
            return JARVISResponse(
                content="A coding objective is required after 'code:'.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "stage": "REQUEST",
                    "success": False,
                },
            )

        if self.coding_agent_service is None:
            return JARVISResponse(
                content="The coding agent is not configured for this JARVIS runtime.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "stage": "UNAVAILABLE",
                    "success": False,
                },
            )

        task = CodingAgentTask(
            objective=objective,
            metadata={
                "route": "CODING_AGENT",
                **(
                    {"provider_name": provider_name}
                    if provider_name is not None
                    else {}
                ),
            },
        )

        try:
            task = self.coding_agent_service.prepare_task(task)
            plan = self.coding_agent_service.plan(task)
        except (TypeError, ValueError) as exc:
            return JARVISResponse(
                content=f"I could not produce a safe coding plan.\n\n{exc}",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "stage": "PLANNING",
                    "success": False,
                    "task_id": task.task_id,
                },
            )

        pending = self.coding_confirmation_service.stage(task, plan)
        files = tuple(edit.path for edit in plan.edits)
        verification = plan.verification.runner
        if plan.verification.arguments:
            verification += " " + " ".join(plan.verification.arguments)
        if plan.verification.runner == "npm_build":
            verification = "npm run build"

        file_summary = "\n".join(f"- {path}" for path in files) or "- no file edits"
        return JARVISResponse(
            content=(
                "Coding plan ready for approval.\n\n"
                f"Task: {task.objective}\n"
                f"Operation ID: {pending.operation_id}\n"
                f"Plan fingerprint: {pending.metadata['plan_fingerprint']}\n\n"
                f"Files ({len(files)}):\n{file_summary}\n\n"
                f"Verification: {verification}\n\n"
                "Use /CONFIRM to authorize this exact plan or /CANCEL to discard it."
            ),
            ai_response=None,
            context=None,
            metadata={
                "route": "CODING_AGENT",
                "stage": "CONFIRMATION",
                "success": True,
                "task_id": task.task_id,
                "operation_id": pending.operation_id,
                "plan_fingerprint": pending.metadata["plan_fingerprint"],
                "edit_count": len(plan.edits),
                "verification_runner": plan.verification.runner,
                "verification_arguments": plan.verification.arguments,
                "rationale": plan.rationale,
            },
        )

    def _handle_command(self, text: str) -> JARVISResponse:
        parsed = self.command_service.parser.parse(text)
        if parsed is not None and parsed.name == "CONFIRM":
            coding_pending = self.coding_confirmation_service.get_pending()
            if coding_pending is not None:
                return self._confirm_coding(parsed.arguments)
        if parsed is not None and parsed.name == "CANCEL":
            coding_pending = self.coding_confirmation_service.get_pending()
            if coding_pending is not None:
                return self._cancel_coding(parsed.arguments)
        return super()._handle_command(text)

    def _confirm_coding(self, arguments: tuple[str, ...]) -> JARVISResponse:
        if len(arguments) > 1:
            return JARVISResponse(
                content="/CONFIRM accepts zero or one coding operation ID.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "command": "CONFIRM",
                    "success": False,
                },
            )

        operation_id = arguments[0] if arguments else None
        operation = (
            self.coding_confirmation_service.get_pending()
            if operation_id is None
            else self.coding_confirmation_service.get(operation_id)
        )
        if operation is None or not operation.is_pending:
            return JARVISResponse(
                content="No matching pending coding operation was found.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "command": "CONFIRM",
                    "success": False,
                },
            )

        expected = operation.metadata.get("plan_fingerprint")
        actual = coding_plan_fingerprint(operation.task, operation.plan)
        if expected != actual:
            return JARVISResponse(
                content="Coding execution blocked: the approved plan fingerprint no longer matches.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "command": "CONFIRM",
                    "stage": "FINGERPRINT",
                    "success": False,
                    "operation_id": operation.operation_id,
                },
            )

        confirmed = self.coding_confirmation_service.confirm(operation.operation_id)
        if confirmed is None:
            return JARVISResponse(
                content="The coding operation could not be confirmed.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "command": "CONFIRM",
                    "success": False,
                },
            )

        if self.coding_agent_service is None:
            return JARVISResponse(
                content="The coding agent is no longer configured; execution was not attempted.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "command": "CONFIRM",
                    "success": False,
                    "operation_id": confirmed.operation_id,
                },
            )

        execution_task = CodingAgentTask(
            objective=confirmed.task.objective,
            task_id=confirmed.task.task_id,
            metadata={
                **dict(confirmed.task.metadata),
                "coding_operation_id": confirmed.operation_id,
            },
        )
        result = self.coding_agent_service.execute(execution_task, confirmed.plan)
        return JARVISResponse(
            content=(
                f"Coding operation {result.status}.\n\n"
                f"{result.message}"
            ),
            ai_response=None,
            context=None,
            metadata={
                "route": "CODING_AGENT",
                "command": "CONFIRM",
                "stage": "EXECUTION",
                "success": result.successful,
                "operation_id": confirmed.operation_id,
                "task_id": result.task_id,
                "coding_status": result.status,
                "edits_attempted": result.edits_attempted,
                "edits_applied": result.edits_applied,
                "blocked_tool": result.blocked_tool,
                "verification": result.verification,
            },
        )

    def _cancel_coding(self, arguments: tuple[str, ...]) -> JARVISResponse:
        if len(arguments) > 1:
            return JARVISResponse(
                content="/CANCEL accepts zero or one coding operation ID.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "command": "CANCEL",
                    "success": False,
                },
            )

        operation_id = arguments[0] if arguments else None
        operation = self.coding_confirmation_service.cancel(operation_id)
        if operation is None:
            return JARVISResponse(
                content="No matching pending coding operation was found.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "CODING_AGENT",
                    "command": "CANCEL",
                    "success": False,
                },
            )

        return JARVISResponse(
            content=f"Coding operation cancelled.\n\nOperation ID: {operation.operation_id}",
            ai_response=None,
            context=None,
            metadata={
                "route": "CODING_AGENT",
                "command": "CANCEL",
                "success": True,
                "operation_id": operation.operation_id,
                "operation_status": operation.status.value,
            },
        )


__all__ = ["CodingAgentJARVIS"]
