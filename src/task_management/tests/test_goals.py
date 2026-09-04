import unittest

from src.task_management.goals import (
    Goal,
    GoalObjectiveStore,
    Objective,
    ObjectiveState,
    ObjectiveTransitionError,
    Provenance,
)


class GoalObjectiveBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provenance = Provenance(source="user", reference_id="request-1")
        self.goal = Goal(
            goal_id="goal-1",
            title="Build home automation business",
            description="Create a functioning personal business.",
            provenance=self.provenance,
        )
        self.objective = Objective(
            objective_id="objective-1",
            goal_id="goal-1",
            title="Establish first service offering",
            description="Define the initial commercial offering.",
            provenance=self.provenance,
            priority=10,
        )

    def test_goal_and_objective_are_immutable(self) -> None:
        with self.assertRaises((AttributeError, TypeError)):
            self.goal.title = "changed"
        with self.assertRaises((AttributeError, TypeError)):
            self.objective.priority = 1
        with self.assertRaises(TypeError):
            self.objective.metadata["x"] = "y"

    def test_objective_requires_existing_goal_in_store(self) -> None:
        store = GoalObjectiveStore()
        with self.assertRaises(ValueError):
            store.put_objective(self.objective)

    def test_goal_objective_identity_conflicts_are_rejected(self) -> None:
        store = GoalObjectiveStore()
        store.put_goal(self.goal)
        store.put_goal(self.goal)
        store.put_objective(self.objective)
        store.put_objective(self.objective)
        conflicting = Objective(
            objective_id="objective-1",
            goal_id="goal-1",
            title="Different",
            description="Different",
            provenance=self.provenance,
        )
        with self.assertRaises(ValueError):
            store.put_objective(conflicting)

    def test_objective_lifecycle_is_explicit_and_bounded(self) -> None:
        active = self.objective.transition(ObjectiveState.ACTIVE, reference_id="activate-1")
        paused = active.transition(ObjectiveState.PAUSED, reference_id="pause-1")
        resumed = paused.transition(ObjectiveState.ACTIVE, reference_id="resume-1")
        completed = resumed.transition(ObjectiveState.COMPLETED, reference_id="complete-1")

        self.assertEqual(active.state, ObjectiveState.ACTIVE)
        self.assertEqual(paused.state, ObjectiveState.PAUSED)
        self.assertEqual(resumed.state, ObjectiveState.ACTIVE)
        self.assertEqual(completed.state, ObjectiveState.COMPLETED)
        self.assertEqual(completed.metadata["last_transition_reference"], "complete-1")

    def test_terminal_objective_cannot_transition(self) -> None:
        completed = self.objective.transition(ObjectiveState.ACTIVE, reference_id="activate-1").transition(
            ObjectiveState.COMPLETED, reference_id="complete-1"
        )
        with self.assertRaises(ObjectiveTransitionError):
            completed.transition(ObjectiveState.ACTIVE, reference_id="reopen-1")

    def test_invalid_transition_is_rejected(self) -> None:
        with self.assertRaises(ObjectiveTransitionError):
            self.objective.transition(ObjectiveState.COMPLETED, reference_id="complete-1")

    def test_transition_requires_reference(self) -> None:
        with self.assertRaises(ValueError):
            self.objective.transition(ObjectiveState.ACTIVE, reference_id="")

    def test_objective_context_is_non_authoritative(self) -> None:
        context = self.objective.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_goal_context_is_non_authoritative(self) -> None:
        context = self.goal.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])

    def test_objectives_are_ranked_deterministically(self) -> None:
        store = GoalObjectiveStore()
        store.put_goal(self.goal)
        store.put_objective(self.objective)
        store.put_objective(
            Objective(
                objective_id="objective-2",
                goal_id="goal-1",
                title="Second",
                description="Second objective.",
                provenance=self.provenance,
                priority=20,
                state=ObjectiveState.ACTIVE,
            )
        )
        self.assertEqual(
            tuple(item.objective_id for item in store.list_objectives("goal-1")),
            ("objective-2", "objective-1"),
        )

    def test_terminal_filter_excludes_completed_cancelled_and_superseded(self) -> None:
        store = GoalObjectiveStore()
        store.put_goal(self.goal)
        active = self.objective.transition(ObjectiveState.ACTIVE, reference_id="activate-1")
        store.put_objective(active)
        completed = active.transition(ObjectiveState.COMPLETED, reference_id="complete-1")
        store.replace_objective(completed)
        other = Objective(
            objective_id="objective-2",
            goal_id="goal-1",
            title="Other",
            description="Other objective.",
            provenance=self.provenance,
            state=ObjectiveState.CANCELLED,
        )
        store.put_objective(other)

        current = store.list_objectives("goal-1", include_terminal=False)
        self.assertEqual(current, ())


if __name__ == "__main__":
    unittest.main()
