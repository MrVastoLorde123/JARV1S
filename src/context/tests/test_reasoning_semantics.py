import unittest

from src.context.context_source_selection import ContextSource, ContextSourceSelector
from src.context.models import EVIDENCE, MEMORY, OBSERVATION, ContextItem, ContextPackage
from src.context.reasoning_semantics import (
    EpistemicRole,
    Freshness,
    ReasoningContext,
    ReasoningContextProjector,
    ReasoningInput,
)
from src.context.working_context import WorkingContext
from src.core.conversation_models import StateSnapshot, Turn
from src.core.execution_executor_models import PlanExecutionStatus
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.task_models import TaskRequest, TaskType


class ReasoningSemanticsTests(unittest.TestCase):
    def _state(self):
        return StateSnapshot(
            conversation_id="conversation-1",
            created_at="2026-09-01T00:00:00Z",
            updated_at="2026-09-01T00:01:00Z",
            turns=(Turn("user", "inspect config", "2026-09-01T00:01:00Z"),),
            active_topic="JARVIS",
            active_task="inspect configuration",
        )

    def _execution_state(self):
        return ExecutionState(
            goal="inspect config",
            plan_id="plan-1",
            status=PlanExecutionStatus.COMPLETED,
            completed_steps=("inspect",),
            next_allowed_actions=("COMPLETE",),
        )

    def _working_context(self, *, selection=None):
        package = ContextPackage(
            request="inspect config",
            items=(
                ContextItem(
                    source_type=MEMORY,
                    content="The config is stored under src/core.",
                    relevance_score=0.9,
                    confidence=0.8,
                    importance=0.7,
                    provenance={"source_id": "memory-store", "memory_id": "m-1"},
                ),
                ContextItem(
                    source_type=EVIDENCE,
                    content="Previous inspection found config.py.",
                    relevance_score=1.0,
                    confidence=1.0,
                    provenance={"source_id": "evidence-store"},
                ),
            ),
            instructions=("Do not invent information.",),
            metadata={"context_version": "1"},
        )
        execution = self._execution_state()
        return WorkingContext(
            request="inspect config",
            context_package=package,
            conversation_state=self._state(),
            task=TaskRequest("inspect config", TaskType.INFORMATION),
            execution_state=execution,
            execution_progress=ExecutionProgress.from_state(execution),
            observations=(ContextItem(OBSERVATION, "config.py exists"),),
            source_selection=selection,
            metadata={"runtime": "v1"},
        )

    def test_roles_distinguish_persisted_claims_evidence_and_observations(self):
        working = self._working_context()
        reasoning = ReasoningContextProjector().project(working)

        self.assertEqual(reasoning.inputs[0].epistemic_role, EpistemicRole.PERSISTED_CLAIM)
        self.assertEqual(reasoning.inputs[1].epistemic_role, EpistemicRole.EVIDENCE)
        self.assertEqual(reasoning.observations[0].epistemic_role, EpistemicRole.OBSERVED)
        self.assertFalse(reasoning.inputs[0].authority_allowed)
        self.assertFalse(reasoning.inputs[1].authority_allowed)
        self.assertTrue(reasoning.observations[0].authority_allowed)
        self.assertNotIn(reasoning.observations[0], reasoning.inputs)

    def test_selected_source_can_be_authoritative_only_when_selector_allows_it(self):
        sources = (
            ContextSource("memory-store", MEMORY, relevance_score=1.0),
            ContextSource("evidence-store", EVIDENCE, relevance_score=1.0),
        )
        selection = ContextSourceSelector().select("inspect config", sources)
        working = self._working_context(selection=selection)
        reasoning = ReasoningContextProjector().project(working)

        self.assertTrue(all(item.authority_allowed for item in reasoning.inputs))
        self.assertTrue(all(item.freshness is Freshness.UNKNOWN for item in reasoning.inputs))

    def test_stale_selected_source_loses_authoritative_reuse(self):
        sources = (
            ContextSource(
                source_id="memory-store",
                source_type=MEMORY,
                relevance_score=1.0,
                last_refreshed_at=0.0,
                refresh_interval_seconds=10.0,
            ),
            ContextSource("evidence-store", EVIDENCE, relevance_score=1.0),
        )
        selection = ContextSourceSelector().select(
            "inspect config",
            sources,
            now=20.0,
        )
        working = self._working_context(selection=selection)
        reasoning = ReasoningContextProjector().project(working)

        memory_input = next(item for item in reasoning.inputs if item.source_type == MEMORY)
        evidence_input = next(item for item in reasoning.inputs if item.source_type == EVIDENCE)

        self.assertEqual(memory_input.freshness, Freshness.STALE)
        self.assertFalse(memory_input.authority_allowed)
        self.assertTrue(evidence_input.authority_allowed)
        self.assertIn("memory-store", selection.refresh_required)

    def test_current_state_contains_conversation_task_and_execution_context(self):
        reasoning = ReasoningContextProjector().project(self._working_context())

        self.assertEqual(reasoning.current_state["conversation"]["active_task"], "inspect configuration")
        self.assertEqual(reasoning.current_state["task"]["task_type"], "INFORMATION")
        self.assertEqual(reasoning.current_state["execution_state"]["status"], "COMPLETED")
        self.assertEqual(reasoning.current_state["execution_progress"]["attempt_count"], 1)

    def test_derived_and_proposed_are_output_only_roles(self):
        with self.assertRaises(ValueError):
            ReasoningInput(
                content="inference",
                source_type="MODEL",
                epistemic_role=EpistemicRole.DERIVED,
            )
        with self.assertRaises(ValueError):
            ReasoningInput(
                content="do X",
                source_type="MODEL",
                epistemic_role=EpistemicRole.PROPOSED,
            )

    def test_stale_input_cannot_claim_authority(self):
        with self.assertRaises(ValueError):
            ReasoningInput(
                content="stale claim",
                source_type=MEMORY,
                freshness=Freshness.STALE,
                authority_allowed=True,
                epistemic_role=EpistemicRole.PERSISTED_CLAIM,
            )

    def test_reasoning_context_serialization_is_provider_neutral(self):
        reasoning = ReasoningContextProjector().project(self._working_context())
        context = reasoning.to_context()

        self.assertEqual(context["request"], "inspect config")
        self.assertEqual(context["inputs"][0]["epistemic_role"], "persisted_claim")
        self.assertEqual(context["inputs"][1]["epistemic_role"], "evidence")
        self.assertEqual(context["observations"][0]["epistemic_role"], "observed")
        self.assertIn("authority_allowed", context["inputs"][0])
        self.assertEqual(context["metadata"]["reasoning_semantics"], "m7.1")

    def test_projector_rejects_non_working_context(self):
        with self.assertRaises(TypeError):
            ReasoningContextProjector().project({"request": "inspect config"})

    def test_reasoning_context_rejects_non_observed_observations(self):
        item = ReasoningInput(
            content="claim",
            source_type=MEMORY,
            epistemic_role=EpistemicRole.PERSISTED_CLAIM,
        )
        with self.assertRaises(ValueError):
            ReasoningContext("inspect config", (), observations=(item,))


if __name__ == "__main__":
    unittest.main()
