import unittest

from src.agency.worker_context import WorkerContext, WorkerContextProjector
from src.agency.workforce import WorkerAssignment, WorkerDefinition
from src.context.models import ContextItem, ContextPackage
from src.context.working_context import WorkingContext


class WorkerContextTests(unittest.TestCase):
    def setUp(self):
        self.worker = WorkerDefinition(
            worker_id="researcher",
            name="Research Worker",
            capabilities=("search", "summarize"),
            max_steps=5,
        )
        self.global_context = WorkingContext(
            request="research JARVIS architecture",
            context_package=ContextPackage(
                request="research JARVIS architecture",
                items=(
                    ContextItem(source_type="FACT", content="public fact", relevance_score=1.0),
                    ContextItem(source_type="MEMORY", content="private memory", relevance_score=0.9, provenance={"source_id": "memory-1"}),
                ),
                instructions=("be accurate",),
            ),
        )

    def assignment(self, **overrides):
        values = {
            "assignment_id": "assignment-1",
            "worker_id": "researcher",
            "objective": "research a topic",
            "allowed_capabilities": ("search",),
            "input_scope": ("request", "context_items"),
            "output_scope": ("findings",),
            "max_steps": 3,
        }
        values.update(overrides)
        return WorkerAssignment(**values)

    def test_projection_includes_only_requested_fields(self):
        context = WorkerContextProjector().project(
            self.worker, self.assignment(input_scope=("request",)), self.global_context
        )
        self.assertEqual(tuple(context.inputs), ("request",))
        self.assertEqual(context.inputs["request"], "research JARVIS architecture")

    def test_unrequested_global_fields_are_not_projected(self):
        context = WorkerContextProjector().project(
            self.worker, self.assignment(input_scope=("request",)), self.global_context
        )
        self.assertNotIn("context_items", context.inputs)
        self.assertNotIn("instructions", context.inputs)
        self.assertNotIn("observations", context.inputs)
        self.assertNotIn("task", context.inputs)

    def test_projection_is_immutable(self):
        context = WorkerContextProjector().project(self.worker, self.assignment(), self.global_context)
        with self.assertRaises(TypeError):
            context.inputs["request"] = "mutated"
        with self.assertRaises(TypeError):
            context.metadata["global_context_access"] = True

    def test_projection_does_not_grant_authority_or_global_access(self):
        serialized = WorkerContextProjector().project(
            self.worker, self.assignment(), self.global_context
        ).to_context()
        self.assertFalse(serialized["authority_granted"])
        self.assertFalse(serialized["global_context_access"])

    def test_unknown_input_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            WorkerContextProjector().project(
                self.worker, self.assignment(input_scope=("request", "secrets")), self.global_context
            )

    def test_assignment_worker_identity_must_match(self):
        other = WorkerDefinition(
            worker_id="writer",
            name="Writer",
            capabilities=("summarize",),
            max_steps=3,
        )
        with self.assertRaises(ValueError):
            WorkerContextProjector().project(other, self.assignment(), self.global_context)

    def test_worker_context_requires_structured_identity(self):
        with self.assertRaises(ValueError):
            WorkerContext(worker_id="", assignment_id="a", objective="o")


if __name__ == "__main__":
    unittest.main()
