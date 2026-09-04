import json
import unittest

from src.self_development import (
    MAX_LIST_ITEMS,
    SelfDevelopmentProposal,
    SelfDevelopmentValidationError,
)


class SelfDevelopmentProposalTests(unittest.TestCase):
    def make_proposal(self, **overrides):
        values = {
            "proposal_id": "sd-1",
            "title": "Improve retrieval",
            "description": "Improve retrieval quality for repeated project context.",
            "target": "knowledge retrieval",
            "rationale": "Observed repeated retrieval misses suggest an improvement opportunity.",
            "expected_change": "Refine retrieval scoring while preserving existing authority boundaries.",
            "affected_paths": ("src/knowledge/retrieval.py",),
            "validation_requirements": ("run knowledge tests",),
            "rollback_plan": "Revert the change commit if validation or observation fails.",
            "reversible": True,
        }
        values.update(overrides)
        return SelfDevelopmentProposal(**values)

    def test_valid_proposal(self):
        item = self.make_proposal()
        self.assertEqual(item.proposal_id, "sd-1")
        self.assertTrue(item.reversible)

    def test_is_immutable(self):
        item = self.make_proposal()
        with self.assertRaises(Exception):
            item.title = "Changed"

    def test_rejects_non_tuple_affected_paths(self):
        with self.assertRaises(SelfDevelopmentValidationError):
            self.make_proposal(affected_paths=["src/x.py"])

    def test_rejects_duplicate_affected_paths(self):
        with self.assertRaises(SelfDevelopmentValidationError):
            self.make_proposal(affected_paths=("src/x.py", "src/x.py"))

    def test_rejects_duplicate_validation_requirements(self):
        with self.assertRaises(SelfDevelopmentValidationError):
            self.make_proposal(validation_requirements=("test", "test"))

    def test_affected_paths_bounded(self):
        paths = tuple(f"src/{i}.py" for i in range(MAX_LIST_ITEMS + 1))
        with self.assertRaises(SelfDevelopmentValidationError):
            self.make_proposal(affected_paths=paths)

    def test_add_affected_path_is_functional(self):
        item = self.make_proposal(affected_paths=())
        updated = item.with_affected_path("src/new.py")
        self.assertEqual(item.affected_paths, ())
        self.assertEqual(updated.affected_paths, ("src/new.py",))

    def test_duplicate_affected_path_rejected_when_added(self):
        item = self.make_proposal(affected_paths=("src/new.py",))
        with self.assertRaises(SelfDevelopmentValidationError):
            item.with_affected_path("src/new.py")

    def test_add_validation_requirement_is_functional(self):
        item = self.make_proposal(validation_requirements=())
        updated = item.with_validation_requirement("run core tests")
        self.assertEqual(item.validation_requirements, ())
        self.assertEqual(updated.validation_requirements, ("run core tests",))

    def test_reversible_requires_rollback_plan(self):
        with self.assertRaises(SelfDevelopmentValidationError):
            self.make_proposal(rollback_plan="")

    def test_non_reversible_without_rollback_is_allowed(self):
        item = self.make_proposal(reversible=False, rollback_plan="")
        self.assertFalse(item.reversible)

    def test_serialization_is_non_authoritative(self):
        data = self.make_proposal().to_dict()
        self.assertTrue(data["self_change_proposed"])
        self.assertFalse(data["instruction_granted"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["confirmation_granted"])
        self.assertFalse(data["execution_requested"])
        self.assertFalse(data["authority_scope_change"])
        self.assertFalse(data["identity_change_authorized"])

    def test_json_round_trip(self):
        data = json.loads(self.make_proposal().to_json())
        self.assertEqual(data["proposal_id"], "sd-1")
        self.assertIsInstance(data, dict)

    def test_empty_required_text_rejected(self):
        for field in ("proposal_id", "title", "description", "target", "rationale", "expected_change"):
            with self.subTest(field=field):
                with self.assertRaises(SelfDevelopmentValidationError):
                    self.make_proposal(**{field: ""})

    def test_non_bool_reversible_rejected(self):
        with self.assertRaises(SelfDevelopmentValidationError):
            self.make_proposal(reversible="yes")

    def test_metadata_is_frozen(self):
        item = self.make_proposal(metadata={"nested": {"value": 1}})
        with self.assertRaises(TypeError):
            item.metadata["nested"]["value"] = 2


if __name__ == "__main__":
    unittest.main()
