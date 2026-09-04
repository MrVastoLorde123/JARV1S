import json
import unittest

from src.initiative import InitiativeCandidate, InitiativeValidationError, MAX_REFERENCES


class InitiativeCandidateTests(unittest.TestCase):
    def test_valid_candidate(self):
        item = InitiativeCandidate(
            "init-1", "Review project", "The project may need review.",
            context_refs=("project:p1",), tags=("project",), metadata={"source": "context"}
        )
        self.assertEqual(item.initiative_id, "init-1")
        self.assertEqual(item.context_refs, ("project:p1",))

    def test_is_immutable(self):
        item = InitiativeCandidate("init-1", "Review", "Review this.")
        with self.assertRaises(Exception):
            item.title = "Changed"

    def test_metadata_is_frozen(self):
        item = InitiativeCandidate("init-1", "Review", "Review this.", metadata={"a": {"b": 1}})
        with self.assertRaises(TypeError):
            item.metadata["a"]["b"] = 2

    def test_context_refs_must_be_tuple(self):
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "Review", "Review this.", context_refs=["x"])

    def test_context_refs_unique(self):
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "Review", "Review this.", context_refs=("x", "x"))

    def test_tags_unique(self):
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "Review", "Review this.", tags=("x", "x"))

    def test_context_refs_bounded(self):
        refs = tuple(f"r{i}" for i in range(MAX_REFERENCES + 1))
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "Review", "Review this.", context_refs=refs)

    def test_add_context_ref_functional(self):
        item = InitiativeCandidate("init-1", "Review", "Review this.")
        updated = item.with_context_ref("project:p1")
        self.assertEqual(item.context_refs, ())
        self.assertEqual(updated.context_refs, ("project:p1",))

    def test_add_duplicate_context_ref_rejected(self):
        item = InitiativeCandidate("init-1", "Review", "Review this.", context_refs=("p1",))
        with self.assertRaises(InitiativeValidationError):
            item.with_context_ref("p1")

    def test_add_tag_functional(self):
        item = InitiativeCandidate("init-1", "Review", "Review this.")
        updated = item.with_tag("planning")
        self.assertEqual(item.tags, ())
        self.assertEqual(updated.tags, ("planning",))

    def test_serialization_explicitly_non_authoritative(self):
        data = InitiativeCandidate("init-1", "Review", "Review this.").to_dict()
        self.assertFalse(data["initiative_is_instruction"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])
        self.assertFalse(data["user_intent_guaranteed"])

    def test_json_round_trip_shape(self):
        data = json.loads(InitiativeCandidate("init-1", "Review", "Review this.").to_json())
        self.assertEqual(data["initiative_id"], "init-1")
        self.assertIsInstance(data, dict)

    def test_empty_title_rejected(self):
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "", "Review this.")

    def test_empty_description_rejected(self):
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "Review", "")

    def test_non_mapping_metadata_rejected(self):
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "Review", "Review this.", metadata="bad")

    def test_unsupported_nested_metadata_rejected(self):
        with self.assertRaises(InitiativeValidationError):
            InitiativeCandidate("init-1", "Review", "Review this.", metadata={"bad": object()})


if __name__ == "__main__":
    unittest.main()
