"""OPS-10 autonomous context continuity acceptance."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.ai.service import AIService
from src.core.capability_argument_planner import CapabilityInvocationService
from src.core.conversation import ConversationState
from src.core.conversation_store import ConversationStore
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.jarvis import JARVIS
from src.core.request_intent import IntentKind, RequestIntent
from src.core.tool_execution import ToolCapabilityGateway
from src.runtime.operational_continuous_runtime import OperationalContinuousRuntime
from src.tools.models import RiskLevel, ToolDefinition, ToolRequest, ToolResult


class StaticToolIntentClassifier:
    def classify(self, text):
        return RequestIntent(
            kind=IntentKind.TOOL,
            content=text,
            confidence=0.99,
            reasoning="OPS-10 deterministic continuity fixture",
        )


class EmptyArgumentPlanner:
    def propose(self, intent, capability):
        return {}


class ContinuityToolGateway(ToolCapabilityGateway):
    def __init__(self):
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
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"status": "ops-10-ok"},
            invocation_id=request.invocation_id,
        )


class StubConversationStore(ConversationStore):
    def __init__(self):
        self._records = {}
        self._states = {}
        self._messages = {}

    def get_conversation(self, conversation_id):
        return self._records.get(conversation_id)

    def create_conversation(self, title=None, conversation_id=None):
        conversation_id = conversation_id or f"conversation-{len(self._records) + 1}"
        state = ConversationState(conversation_id=conversation_id)
        self._states[conversation_id] = state
        self._messages.setdefault(conversation_id, [])
        record = SimpleNamespace(
            conversation_id=conversation_id,
            title=title or "JARVIS Conversation",
            created_at=state.snapshot().created_at,
            updated_at=state.snapshot().updated_at,
        )
        self._records[conversation_id] = record
        return record

    def load_state(self, conversation_id):
        state = self._states.get(conversation_id)
        if state is None:
            return None
        return ConversationState.restore(
            conversation_id=conversation_id,
            created_at=state.snapshot().created_at,
            updated_at=state.snapshot().updated_at,
            turns=state.snapshot().turns,
            active_topic=state.snapshot().active_topic,
            active_task=state.snapshot().active_task,
            metadata=state.snapshot().metadata,
        )

    def save_state(self, snapshot):
        self._states[snapshot.conversation_id] = ConversationState.restore(
            conversation_id=snapshot.conversation_id,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
            turns=snapshot.turns,
            active_topic=snapshot.active_topic,
            active_task=snapshot.active_task,
            metadata=snapshot.metadata,
        )
        record = self._records[snapshot.conversation_id]
        record.updated_at = snapshot.updated_at

    def append_message(
        self,
        conversation_id,
        role,
        content,
        parent_id=None,
        message_id=None,
        created_at=None,
    ):
        message_id = message_id or f"message-{len(self._messages[conversation_id]) + 1}"
        created_at = created_at or self._states[conversation_id].snapshot().updated_at
        self._messages.setdefault(conversation_id, []).append(
            {
                "id": message_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "created_at": created_at,
                "parent_id": parent_id,
            }
        )
        return {"message_id": message_id, "created_at": created_at}

    def get_messages(self, conversation_id):
        return [
            (
                item["id"],
                item["conversation_id"],
                item["role"],
                item["content"],
                item["created_at"],
                item["parent_id"],
            )
            for item in self._messages.get(conversation_id, [])
        ]


def db_factory(path: Path):
    return lambda: sqlite3.connect(path)


class OPS10AutonomousContextContinuityTests(unittest.TestCase):
    def test_autonomous_factory_rehydrates_prior_cycle_context(self):
        conversation_store = StubConversationStore()
        gateway = ContinuityToolGateway()
        processors = []

        def processor_factory(job):
            conversation_id = f"autonomous-{job.job_id}"
            if conversation_store.get_conversation(conversation_id) is None:
                conversation_store.create_conversation(
                    title=f"Autonomous {job.goal}",
                    conversation_id=conversation_id,
                )
            processor = JARVIS(
                ai_service=AIService(default_provider="unused"),
                intelligent_request_router=IntelligentRequestRouter(
                    StaticToolIntentClassifier()
                ),
                tool_invoker=gateway,
                capability_invocation_service=CapabilityInvocationService(
                    EmptyArgumentPlanner()
                ),
                conversation_store=conversation_store,
                conversation_id=conversation_id,
                enable_memory_formation=False,
            )
            processors.append(processor)
            return processor

        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "ops-10.db"
            runtime = OperationalContinuousRuntime(
                processor_factory=processor_factory,
                connection_factory=db_factory(database),
            )
            job = runtime.submit(
                "Report the current runtime status.",
                now=100,
                interval=10,
            )

            first = runtime.tick(100)[0]
            self.assertEqual(first.run.job.status.value, "COMPLETED")

            self.assertEqual(len(processors), 1)
            first_turns = processors[0].conversation.snapshot().turns
            self.assertEqual(len(first_turns), 2)
            self.assertEqual(first_turns[0].role, "user")
            self.assertEqual(first_turns[1].role, "assistant")

            second_job = runtime.submit(
                "Continue the current runtime status task.",
                now=110,
                interval=10,
                job_id=f"{job.job_id}-second",
            )
            second = runtime.tick(110)[0]
            self.assertEqual(second.run.job.status.value, "COMPLETED")

            self.assertEqual(len(processors), 2)
            second_turns = processors[1].conversation.snapshot().turns
            self.assertEqual(
                tuple((turn.role, turn.content) for turn in second_turns[:2]),
                tuple((turn.role, turn.content) for turn in first_turns),
            )
            self.assertEqual(gateway.calls.__len__(), 2)
            del second_job

    def test_operational_turn_is_idempotent(self):
        conversation_store = StubConversationStore()
        conversation = conversation_store.create_conversation(
            conversation_id="ops-10-idempotent",
        )
        processor = JARVIS(
            ai_service=AIService(default_provider="unused"),
            conversation_store=conversation_store,
            conversation_id=conversation.conversation_id,
            enable_memory_formation=False,
        )

        processor.record_operational_turn(
            "Autonomous query.",
            "Autonomous answer.",
        )
        processor.record_operational_turn(
            "Autonomous query.",
            "Autonomous answer.",
        )

        turns = processor.conversation.snapshot().turns
        self.assertEqual(len(turns), 2)
        self.assertEqual(turns[0].content, "Autonomous query.")
        self.assertEqual(turns[1].content, "Autonomous answer.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
