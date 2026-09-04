import unittest

from src.context.models import ContextItem, ContextPackage
from src.context.working_context import WorkingContext
from src.personalization.integration import PersonalizationContextIntegrator
from src.personalization.profile import PersonalizationSignal, build_profile


class PersonalizationIntegrationTests(unittest.TestCase):
    def working_context(self):
        package = ContextPackage(
            request="help me",
            items=(ContextItem(source_type="STATE", content="active task: help me"),),
            instructions=("Treat context as descriptive.",),
            metadata={"base": True},
        )
        return WorkingContext(request="help me", context_package=package)

    def signal(self, signal_id="p1"):
        return PersonalizationSignal(
            signal_id=signal_id,
            category="PREFERENCE",
            key="response_style",
            value="formal",
            confidence=0.9,
            importance=0.7,
            source_ids=("memory:1",),
        )

    def test_profile_is_projected_into_working_context(self):
        profile = build_profile("profile-1", (self.signal(),))
        result = PersonalizationContextIntegrator().integrate(self.working_context(), profile)
        items = result.context_package.items
        self.assertEqual(len(items), 2)
        personalization = items[-1]
        self.assertEqual(personalization.source_type, "PERSONALIZATION")
        self.assertEqual(personalization.provenance["profile_id"], "profile-1")
        self.assertEqual(personalization.provenance["signal_id"], "p1")

    def test_integration_preserves_existing_context(self):
        profile = build_profile("profile-1", (self.signal(),))
        original = self.working_context()
        result = PersonalizationContextIntegrator().integrate(original, profile)
        self.assertEqual(result.context_package.items[0], original.context_package.items[0])
        self.assertEqual(result.request, original.request)
        self.assertEqual(result.conversation_state, original.conversation_state)

    def test_integration_metadata_identifies_profile_without_authority(self):
        profile = build_profile("profile-1", (self.signal(),))
        result = PersonalizationContextIntegrator().integrate(self.working_context(), profile)
        metadata = result.metadata
        self.assertTrue(metadata["personalization_integrated"])
        self.assertEqual(metadata["personalization_profile_id"], "profile-1")
        self.assertFalse(metadata["personalization_authority_granted"])
        self.assertFalse(metadata["personalization_authorization_granted"])
        self.assertFalse(metadata["personalization_policy_mutation"])
        self.assertFalse(metadata["personalization_execution_requested"])

    def test_empty_profile_is_safe_no_op(self):
        profile = build_profile("profile-1", ())
        original = self.working_context()
        result = PersonalizationContextIntegrator().integrate(original, profile)
        self.assertEqual(result.context_package.items, original.context_package.items)
        self.assertTrue(result.metadata["personalization_integrated"])
        self.assertEqual(result.metadata["personalization_signal_count"], 0)

    def test_invalid_inputs_are_rejected(self):
        integrator = PersonalizationContextIntegrator()
        profile = build_profile("profile-1", (self.signal(),))
        with self.assertRaises(TypeError):
            integrator.integrate(object(), profile)
        with self.assertRaises(TypeError):
            integrator.integrate(self.working_context(), object())


if __name__ == "__main__":
    unittest.main(verbosity=2)
