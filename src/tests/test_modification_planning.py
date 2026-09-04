"""Focused tests for the M16.3 controlled modification planning boundary."""

import unittest
from dataclasses import FrozenInstanceError

from src.change_impact import ChangeImpactAssessment, ImpactDomain, ImpactLevel
from src.modification_planning import (
    ControlledModificationPlan,
    ModificationPlanValidationError,
    ModificationStep,
    ModificationStepKind,
)
from src.self_development import SelfDevelopmentProposal


class ModificationPlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.proposal = SelfDevelopmentProposal(
            proposal_id="p-1",
            title="Improve planner",
            description="Refine planning logic.",
            target="src/modification_planning.py",
            rationale="Improve deterministic planning.",
            expected_change="Add explicit validation checkpoints.",
            rollback_plan="Revert the planner change.",
        )
        self.assessment = ChangeImpactAssessment(
            assessment_id="a-1",
            proposal=self.proposal,
            overall_impact=ImpactLevel.MEDIUM,
            affected_domains=(ImpactDomain.CODE,),
            reasons=("Planner behavior changes",),
            dependency_impact=ImpactLevel.LOW,
            compatibility_impact=ImpactLevel.LOW,
            rollback_feasibility=ImpactLevel.HIGH,
            confidence=0.9,
        )
        self.step = ModificationStep(
            step_id="s-1",
            kind=ModificationStepKind.INSPECT,
            description="Inspect target files and current tests.",
            validation_gate="Inspection completed.",
            rollback_checkpoint="Before modification.",
        )
        self.plan = ControlledModificationPlan(
            plan_id="plan-1",
            assessment=self.assessment,
            steps=(self.step,),
            validation_gates=("Focused tests pass.",),
            rollback_checkpoints=("Restore known-good revision.",),
            constraints=("No authority change.",),
        )

    def test_lineage_is_preserved(self) -> None:
        self.assertEqual(self.plan.proposal_id, "p-1")
        self.assertEqual(self.plan.assessment_id, "a-1")

    def test_plan_requires_a_step(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            ControlledModificationPlan("plan-x", self.assessment, ())

    def test_steps_are_typed(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            ControlledModificationPlan("plan-x", self.assessment, ("bad",))

    def test_duplicate_step_ids_are_rejected(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            ControlledModificationPlan("plan-x", self.assessment, (self.step, self.step))

    def test_step_fields_are_validated(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            ModificationStep("", ModificationStepKind.TEST, "x", "y")
        with self.assertRaises(ModificationPlanValidationError):
            ModificationStep("s", "test", "x", "y")

    def test_step_validation_gate_is_required(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            ModificationStep("s", ModificationStepKind.TEST, "x", "")

    def test_step_rollback_checkpoint_is_optional(self) -> None:
        step = ModificationStep("s-2", ModificationStepKind.TEST, "Run tests.", "Tests pass.")
        self.assertEqual(step.rollback_checkpoint, "")

    def test_with_step_is_functional(self) -> None:
        step = ModificationStep("s-2", ModificationStepKind.TEST, "Run tests.", "Tests pass.")
        updated = self.plan.with_step(step)
        self.assertEqual(len(self.plan.steps), 1)
        self.assertEqual(len(updated.steps), 2)

    def test_with_duplicate_step_is_rejected(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            self.plan.with_step(self.step)

    def test_with_validation_gate_is_functional(self) -> None:
        updated = self.plan.with_validation_gate("Observe behavior.")
        self.assertEqual(len(self.plan.validation_gates), 1)
        self.assertEqual(len(updated.validation_gates), 2)

    def test_with_duplicate_gate_is_rejected(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            self.plan.with_validation_gate("Focused tests pass.")

    def test_with_rollback_checkpoint_is_functional(self) -> None:
        updated = self.plan.with_rollback_checkpoint("After verification.")
        self.assertEqual(len(self.plan.rollback_checkpoints), 1)
        self.assertEqual(len(updated.rollback_checkpoints), 2)

    def test_with_duplicate_checkpoint_is_rejected(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            self.plan.with_rollback_checkpoint("Restore known-good revision.")

    def test_plan_is_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.plan.plan_id = "changed"

    def test_plan_has_no_authority(self) -> None:
        self.assertFalse(self.plan.authorization_granted)
        self.assertFalse(self.plan.execution_requested)

    def test_authority_review_is_carried_without_granting_authority(self) -> None:
        assessment = ChangeImpactAssessment(
            assessment_id="a-auth",
            proposal=self.proposal,
            overall_impact=ImpactLevel.HIGH,
            affected_domains=(ImpactDomain.CODE, ImpactDomain.AUTHORITY),
            reasons=("Potential authority-boundary effect",),
            authority_scope_impact=True,
            requires_authority_review=True,
            confidence=0.8,
        )
        plan = ControlledModificationPlan("plan-auth", assessment, (self.step,))
        self.assertTrue(plan.requires_authority_review)
        self.assertFalse(plan.authorization_granted)

    def test_serialization_preserves_boundary_flags(self) -> None:
        payload = self.plan.to_dict()
        self.assertTrue(payload["modification_plan"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["instruction_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["authority_scope_change_authorized"])
        self.assertFalse(payload["identity_change_authorized"])

    def test_metadata_is_frozen(self) -> None:
        plan = ControlledModificationPlan(
            "plan-meta",
            self.assessment,
            (self.step,),
            metadata={"owner": {"team": "core"}},
        )
        with self.assertRaises(TypeError):
            plan.metadata["new"] = "value"

    def test_json_is_serializable(self) -> None:
        payload = self.plan.to_json()
        self.assertIn("modification_plan", payload)
        self.assertIn("plan-1", payload)

    def test_constraints_are_bounded_and_unique(self) -> None:
        with self.assertRaises(ModificationPlanValidationError):
            ControlledModificationPlan(
                "plan-x", self.assessment, (self.step,), constraints=("same", "same")
            )


if __name__ == "__main__":
    unittest.main()
