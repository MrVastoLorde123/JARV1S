import json
import unittest

from src.opportunities import (
    DetectionType,
    OpportunityDetection,
    OpportunityDetectionSet,
    OpportunityDetectionValidationError,
    MAX_REFERENCES,
)


class OpportunityDetectionTests(unittest.TestCase):
    def test_valid_detection(self):
        item = OpportunityDetection("d1", DetectionType.OPPORTUNITY, "Review", "A review may help.", context_refs=("project:p1",))
        self.assertEqual(item.detection_type, DetectionType.OPPORTUNITY)

    def test_string_type_coerced(self):
        item = OpportunityDetection("d1", "need", "Review", "A review may help.")
        self.assertIs(item.detection_type, DetectionType.NEED)

    def test_immutable(self):
        item = OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.")
        with self.assertRaises(Exception):
            item.title = "Changed"

    def test_unique_context_refs(self):
        with self.assertRaises(OpportunityDetectionValidationError):
            OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.", context_refs=("x", "x"))

    def test_context_refs_bounded(self):
        refs = tuple(f"r{i}" for i in range(MAX_REFERENCES + 1))
        with self.assertRaises(OpportunityDetectionValidationError):
            OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.", context_refs=refs)

    def test_non_mapping_metadata_rejected(self):
        with self.assertRaises(OpportunityDetectionValidationError):
            OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.", metadata="bad")

    def test_nested_metadata_is_frozen(self):
        item = OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.", metadata={"x": {"y": 1}})
        with self.assertRaises(TypeError):
            item.metadata["x"]["y"] = 2

    def test_unsupported_metadata_rejected(self):
        with self.assertRaises(OpportunityDetectionValidationError):
            OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.", metadata={"x": object()})

    def test_add_context_ref_functional(self):
        item = OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.")
        updated = item.with_context_ref("project:p1")
        self.assertEqual(item.context_refs, ())
        self.assertEqual(updated.context_refs, ("project:p1",))

    def test_duplicate_context_ref_rejected(self):
        item = OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.", context_refs=("project:p1",))
        with self.assertRaises(OpportunityDetectionValidationError):
            item.with_context_ref("project:p1")

    def test_serialization_marks_non_authority(self):
        data = OpportunityDetection("d1", DetectionType.OPPORTUNITY, "Review", "A review may help.").to_dict()
        self.assertFalse(data["truth_guaranteed"])
        self.assertFalse(data["intent_guaranteed"])
        self.assertFalse(data["obligation_created"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])

    def test_json_serializable(self):
        data = json.loads(OpportunityDetection("d1", DetectionType.OPPORTUNITY, "Review", "A review may help.").to_json())
        self.assertIsInstance(data, dict)

    def test_empty_text_rejected(self):
        with self.assertRaises(OpportunityDetectionValidationError):
            OpportunityDetection("d1", DetectionType.NEED, "", "desc")
        with self.assertRaises(OpportunityDetectionValidationError):
            OpportunityDetection("d1", DetectionType.NEED, "title", "")

    def test_set_valid(self):
        item = OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.")
        group = OpportunityDetectionSet((item,))
        self.assertEqual(group.detections, (item,))

    def test_set_unique_ids(self):
        item = OpportunityDetection("d1", DetectionType.NEED, "Review", "A review may help.")
        with self.assertRaises(OpportunityDetectionValidationError):
            OpportunityDetectionSet((item, item))

    def test_set_by_type(self):
        need = OpportunityDetection("d1", DetectionType.NEED, "Review", "Need")
        opportunity = OpportunityDetection("d2", DetectionType.OPPORTUNITY, "Improve", "Opportunity")
        group = OpportunityDetectionSet((need, opportunity))
        self.assertEqual(group.by_type(DetectionType.NEED), (need,))

    def test_set_with_detection_functional(self):
        group = OpportunityDetectionSet()
        item = OpportunityDetection("d1", DetectionType.GAP, "Review", "Gap")
        updated = group.with_detection(item)
        self.assertEqual(group.detections, ())
        self.assertEqual(updated.detections, (item,))

    def test_set_duplicate_rejected(self):
        item = OpportunityDetection("d1", DetectionType.GAP, "Review", "Gap")
        group = OpportunityDetectionSet((item,))
        with self.assertRaises(OpportunityDetectionValidationError):
            group.with_detection(item)

    def test_set_json_serializable(self):
        item = OpportunityDetection("d1", DetectionType.GAP, "Review", "Gap")
        data = json.loads(OpportunityDetectionSet((item,)).to_json())
        self.assertEqual(len(data["detections"]), 1)


if __name__ == "__main__":
    unittest.main()
