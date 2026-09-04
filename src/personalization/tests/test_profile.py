import unittest

from src.personalization.profile import (
    PersonalizationProfile,
    PersonalizationSignal,
    build_profile,
)


class PersonalizationProfileTests(unittest.TestCase):
    def signal(self, signal_id="pref-1", category="PREFERENCE", source_ids=("memory:1",)):
        return PersonalizationSignal(
            signal_id=signal_id,
            category=category,
            key="response_style",
            value="formal",
            confidence=0.9,
            importance=0.7,
            source_ids=source_ids,
        )

    def test_signal_is_immutable_and_non_authoritative(self):
        signal = self.signal()
        self.assertEqual(signal.category, "PREFERENCE")
        with self.assertRaises(AttributeError):
            signal.value = "casual"
        data = signal.to_dict()
        self.assertFalse(data["truth_guaranteed"])
        self.assertFalse(data["authority_granted"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_mutation"])
        self.assertFalse(data["execution_requested"])

    def test_category_is_normalized(self):
        self.assertEqual(self.signal(category="preference").category, "PREFERENCE")

    def test_profile_groups_signals_by_category(self):
        profile = build_profile(
            "profile-1",
            (
                self.signal("p1", "PREFERENCE"),
                self.signal("b1", "BEHAVIOR", ("memory:2",)),
                self.signal("w1", "WORKING_STYLE", ("memory:3",)),
            ),
        )
        self.assertEqual(len(profile.preferences), 1)
        self.assertEqual(len(profile.behaviors), 1)
        self.assertEqual(len(profile.working_style), 1)
        self.assertEqual(profile.for_key("response_style")[0].signal_id, "p1")

    def test_duplicate_signal_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            build_profile("profile-1", (self.signal(), self.signal()))

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValueError):
            self.signal(category="AUTHORIZATION")

    def test_missing_provenance_is_rejected(self):
        with self.assertRaises(ValueError):
            self.signal(source_ids=())

    def test_profile_is_immutable(self):
        profile = build_profile("profile-1", (self.signal(),))
        with self.assertRaises(AttributeError):
            profile.profile_id = "other"

    def test_source_ids_are_explicit(self):
        signal = self.signal()
        self.assertEqual(signal.source_ids, ("memory:1",))
        self.assertEqual(signal.metadata, {})

    def test_profile_projection_remains_non_authoritative(self):
        profile = build_profile("profile-1", (self.signal(),))
        data = profile.to_dict()
        self.assertFalse(data["truth_guaranteed"])
        self.assertFalse(data["authority_granted"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_mutation"])
        self.assertFalse(data["execution_requested"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
