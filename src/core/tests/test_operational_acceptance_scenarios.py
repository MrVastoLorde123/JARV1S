"""End-to-end operational acceptance scenarios for the living JARVIS runtime."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.agents.coding_service import CodingAgentService
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentTask,
    CodingAgentVerification,
    CodingAgentWorker,
)
from src.ai.service import AIService
from src.core.capability_argument_planner import CapabilityInvocationService
from src.core.canonical_cognitive_runtime import CanonicalCognitiveRuntime
from src.core.conversation_store import ConversationStore
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.request_intent import IntentKind, RequestIntent
from src.core.tool_execution import ToolCapabilityGateway
from src.runtime.autonomous_job import AutonomousJobStatus
from src.runtime.operational_continuous_runtime import OperationalContinuousRuntime
from src.core.coding_agent_jarvis import CodingAgentJARVIS
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult


class StaticToolIntentClassifier:
    def classify(self, text):
        return RequestIntent(
            kind=IntentKind.TOOL,
            content=text,
            confidence=0.99,
            reasoning="operational acceptance deterministic tool fixture",
        )


class EmptyArgumentPlanner:
    def propose(self, intent, capability):
        return {}


class AcceptanceToolGateway(ToolCapabilityGateway):
    def __init__(self, *, fail_first: bool = False):
        self.fail_first = fail_first
        self.calls = []

    def list_definitions(self):
        return (
            ToolDefinition(
                name="report_status",
                description="Report the current runtime status.",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.LOW,
            ),
        )

    def invoke(self, request: ToolRequest):
        self.calls.append(request)
        if self.fail_first and len(self.calls) == 1:
            from src.tools.models import ToolError

            return ToolResult(
                success=False,
                tool_name=request.tool_name,
                error=ToolError(
                    code="acceptance_failure",
                    message="simulated first execution failure",
                ),
                invocation_id=request.invocation_id,
            )
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "acceptance-ok"},
            invocation_id=request.invocation_id,
        )


class StaticCodingPlanner:
    def plan(self, task: CodingAgentTask) -> CodingAgentPlan:
        return CodingAgentPlan(
            edits=(
                CodingAgentEdit(
                    path="acceptance/verified.txt",
                    content="confirmed operational change",
                    overwrite=True,
                ),
            ),
            verification=CodingAgentVerification(
                runner="python_unittest",
                arguments=("src/core/tests/test_operational_acceptance_scenarios.py",),
            ),
            rationale="deterministic acceptance scenario plan",
        )


class RecordingCodingInvoker:
    def __init__(self):
        self.calls = []
        self.state = {}

    def invoke(self, request: ToolRequest) -> ToolResult:
        self.calls.append(request)
        if request.tool_name == "write_file":
            self.state[request.arguments["path"]] = request.arguments["content"]
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"accepted": True},
            invocation_id=request.invocation_id,
        )


class ScriptedProcessor:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def ask(self, query):
        self.calls.append(query)
        if not self.responses:
            raise AssertionError("no scripted autonomous response remains")
        return self.responses.pop(0)


class FakeResponse:
    def __init__(self, content, metadata):
        self.content = content
        self.metadata = metadata


def sqlite_factory(path: Path):
    return lambda: sqlite3.connect(path)


def make_live_jarvis(gateway: ToolCapabilityGateway, *, cognitive_runtime=None):
    return JARVIS(
        ai_service=AIService(default_provider="unused"),
        intelligent_request_router=IntelligentRequestRouter(
            StaticToolIntentClassifier()
        ),
        cognitive_runtime=cognitive_runtime,
        tool_invoker=gateway,
        capability_invocation_service=CapabilityInvocationService(
            EmptyArgumentPlanner()
        ),
    )


class LivingJARVISOperationalAcceptanceTests(unittest.TestCase):
    def test_01_persistent_memory_continuity_survives_runtime_restart(self):
        store = ConversationStore()
        conversation = store.create_conversation(
            title="Operational acceptance continuity",
        )
        store.append_message(
            conversation.conversation_id,
            role="user",
            content="I am building JARVIS.",
        )

        first_runtime = JARVIS(
            ai_service=AIService(default_provider="unused"),
            conversation_store=store,
            conversation_id=conversation.conversation_id,
        )
        first_turns = first_runtime.conversation.snapshot().turns
        self.assertEqual(first_turns[-1].content, "I am building JARVIS.")

        restarted_runtime = JARVIS(
            ai_service=AIService(default_provider="unused"),
            conversation_store=store,
            conversation_id=conversation.conversation_id,
        )
        restarted_turns = restarted_runtime.conversation.snapshot().turns

        self.assertEqual(
            tuple((turn.role, turn.content) for turn in restarted_turns),
            tuple((turn.role, turn.content) for turn in first_turns),
        )

    def test_02_useful_read_discovery_work_reaches_real_capability_execution(self):
        gateway = AcceptanceToolGateway()
        jarvis = make_live_jarvis(gateway)

        response = jarvis.ask("Report the current runtime status.")

        self.assertEqual(response.metadata["route"], "TASK")
        self.assertEqual(response.metadata["stage"], "EXECUTION")
        self.assertEqual(response.metadata["execution_status"], "COMPLETED")
        self.assertEqual(response.metadata["capability"], "report_status")
        self.assertEqual(response.metadata["execution_outputs"], ({"status": "acceptance-ok"},))
        self.assertEqual(len(gateway.calls), 1)

        cognitive = response.metadata["cognitive_context"]
        self.assertFalse(cognitive["authority_granted"])
        self.assertFalse(cognitive["authorization_granted"])
        self.assertFalse(cognitive["execution_requested"])

    def test_03_confirmed_state_change_requires_confirmation_then_executes(self):
        planner = StaticCodingPlanner()
        invoker = RecordingCodingInvoker()
        worker = CodingAgentWorker(planner, invoker)
        service = CodingAgentService(planner=planner, worker=worker)
        jarvis = CodingAgentJARVIS(
            ai_service=AIService(default_provider="unused"),
            coding_agent_service=service,
        )

        staged = jarvis.ask("code: apply the accepted operational change")

        self.assertEqual(staged.metadata["stage"], "CONFIRMATION")
        self.assertTrue(staged.metadata["success"])
        self.assertEqual(len(invoker.calls), 0)
        self.assertEqual(invoker.state, {})

        confirmed = jarvis.ask(f"/CONFIRM {staged.metadata['operation_id']}")

        self.assertEqual(confirmed.metadata["stage"], "EXECUTION")
        self.assertTrue(confirmed.metadata["success"])
        self.assertEqual(confirmed.metadata["coding_status"], "verified")
        self.assertEqual(len(invoker.calls), 2)
        self.assertEqual(
            invoker.state["acceptance/verified.txt"],
            "confirmed operational change",
        )
        self.assertEqual(invoker.calls[0].tool_name, "write_file")
        self.assertEqual(invoker.calls[1].tool_name, "run_test")

    def test_04_execution_failure_enters_bounded_recovery_then_completes(self):
        gateway = AcceptanceToolGateway(fail_first=True)
        processor = make_live_jarvis(gateway)
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "ops.db"
            runtime = OperationalContinuousRuntime(
                processor,
                connection_factory=sqlite_factory(database),
                max_recovery_attempts=1,
            )

            job = runtime.submit(
                "Report the current runtime status.",
                now=100,
                interval=10,
            )

            first = runtime.tick(100)[0]
            self.assertEqual(first.run.job.status, AutonomousJobStatus.RUNNING)
            self.assertEqual(
                first.run.job.working_context["recovery_attempts"],
                1,
            )

            second = runtime.tick(110)[0]
            self.assertEqual(second.run.job.status, AutonomousJobStatus.COMPLETED)
            self.assertEqual(len(gateway.calls), 2)
            self.assertEqual(
                second.run.job.status,
                AutonomousJobStatus.COMPLETED,
            )

    def test_05_long_horizon_waiting_work_survives_restart_and_resumes_explicitly(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "ops.db"

            first = ScriptedProcessor(
                [
                    FakeResponse(
                        "additional input required",
                        {
                            "route": "TASK",
                            "stage": "CAPABILITY_SELECTION",
                        },
                    )
                ]
            )
            first_runtime = OperationalContinuousRuntime(
                first,
                connection_factory=sqlite_factory(database),
            )
            job = first_runtime.submit(
                "Continue the protected operational objective.",
                now=100,
                interval=10,
            )
            waiting = first_runtime.tick(100)[0]
            self.assertEqual(
                waiting.run.job.status,
                AutonomousJobStatus.WAITING_INPUT,
            )
            first_runtime.stop()

            second = ScriptedProcessor(
                [
                    FakeResponse(
                        "long-horizon objective completed",
                        {
                            "route": "TASK",
                            "stage": "EXECUTION",
                            "execution_status": "COMPLETED",
                        },
                    )
                ]
            )
            second_runtime = OperationalContinuousRuntime(
                second,
                connection_factory=sqlite_factory(database),
            )

            restored = second_runtime.inspect(job.job_id)
            self.assertEqual(
                restored.status,
                AutonomousJobStatus.WAITING_INPUT,
            )
            self.assertEqual(len(second.calls), 0)

            resumed = second_runtime.resume(
                job.job_id,
                input_context={"operator_input": "proceed with the approved bounded path"},
                now=200,
                interval=10,
            )
            self.assertEqual(resumed.status, AutonomousJobStatus.RUNNING)

            completed = second_runtime.tick(200)[0]
            self.assertEqual(
                completed.run.job.status,
                AutonomousJobStatus.COMPLETED,
            )
            self.assertEqual(len(second.calls), 1)

    def test_06_outcome_driven_learning_changes_later_advisory_behavior_without_authority_expansion(self):
        gateway = AcceptanceToolGateway(fail_first=True)
        cognition = CanonicalCognitiveRuntime(
            clock=lambda: datetime(
                2026,
                9,
                18,
                14,
                0,
                tzinfo=timezone.utc,
            )
        )
        jarvis = make_live_jarvis(
            gateway,
            cognitive_runtime=cognition,
        )

        first = jarvis.ask("Report the current runtime status.")
        self.assertEqual(first.metadata["execution_status"], "FAILED")
        self.assertEqual(
            first.metadata["operational_learning"]["adaptation_hint_status"],
            "CORRECT_PATTERN",
        )

        second = jarvis.ask("Report the current runtime status.")
        self.assertEqual(second.metadata["execution_status"], "COMPLETED")

        step_description = second.metadata["cognitive_context"]["selected_plan"]["steps"][0]["description"]
        self.assertIn(
            "Prior operational learning guidance:",
            step_description,
        )
        self.assertIn(
            "consider correction before repeating",
            step_description,
        )
        self.assertFalse(second.metadata["cognitive_context"]["authority_granted"])
        self.assertFalse(second.metadata["cognitive_context"]["authorization_granted"])
        self.assertFalse(second.metadata["cognitive_context"]["execution_requested"])
        self.assertEqual(len(gateway.calls), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
