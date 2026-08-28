import unittest

from src.memory.memory_decision_models import (
    CREATE,
    MemoryDecision,
    MemoryDecisionContext,
)

from src.memory.memory_decision_provider import (
    MemoryDecisionProvider,
)

from src.memory.memory_decision import (
    MemoryDecisionService,
)

from src.memory.memory_models import (
    CandidateMemory,
)

class FakeDecisionProvider(
    MemoryDecisionProvider
):

    def __init__(
        self,
        name="fake",
    ):
        self._name = name

    def decide(
        self,
        context,
    ):

        return MemoryDecision(
            action=CREATE,
            candidate=context.candidate,
            memory_id=None,
            reason="Fake decision.",
            confidence=0.90,
        )

    def provider_name(
        self,
    ):

        return self._name


class InvalidDecisionProvider(
    MemoryDecisionProvider
):

    def decide(
        self,
        context,
    ):

        return "not a decision"

    def provider_name(
        self,
    ):

        return "invalid"


class MemoryDecisionServiceTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):

        self.candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

        self.context = (
            MemoryDecisionContext(
                candidate=self.candidate,
            )
        )

    def test_provider_can_be_registered(
        self,
    ):

        service = (
            MemoryDecisionService()
        )

        provider = FakeDecisionProvider()

        service.register_provider(
            provider
        )

        self.assertIn(
            "fake",
            service.provider_names(),
        )

    def test_first_provider_becomes_default(
        self,
    ):

        service = (
            MemoryDecisionService()
        )

        service.register_provider(
            FakeDecisionProvider()
        )

        decision = service.decide(
            self.context
        )

        self.assertEqual(
            decision.action,
            CREATE,
        )

    def test_explicit_default_provider_is_used(
        self,
    ):

        service = (
            MemoryDecisionService(
                default_provider="fake"
            )
        )

        service.register_provider(
            FakeDecisionProvider()
        )

        decision = service.decide(
            self.context
        )

        self.assertEqual(
            decision.action,
            CREATE,
        )

    def test_specific_provider_can_be_selected(
        self,
    ):

        service = (
            MemoryDecisionService(
                default_provider="fake-a"
            )
        )

        service.register_provider(
            FakeDecisionProvider(
                name="fake-a"
            )
        )

        service.register_provider(
            FakeDecisionProvider(
                name="fake-b"
            )
        )

        decision = service.decide(
            self.context,
            provider_name="fake-b",
        )

        self.assertEqual(
            decision.action,
            CREATE,
        )

    def test_no_default_provider_is_rejected(
        self,
    ):

        service = (
            MemoryDecisionService()
        )

        with self.assertRaises(
            ValueError
        ):

            service.decide(
                self.context
            )

    def test_unknown_provider_is_rejected(
        self,
    ):

        service = (
            MemoryDecisionService(
                default_provider="fake"
            )
        )

        with self.assertRaises(
            ValueError
        ):

            service.decide(
                self.context
            )

    def test_invalid_provider_type_is_rejected(
        self,
    ):

        service = (
            MemoryDecisionService()
        )

        with self.assertRaises(
            TypeError
        ):

            service.register_provider(
                object()
            )

    def test_invalid_provider_result_is_rejected(
        self,
    ):

        service = (
            MemoryDecisionService(
                default_provider="invalid"
            )
        )

        service.register_provider(
            InvalidDecisionProvider()
        )

        with self.assertRaises(
            TypeError
        ):

            service.decide(
                self.context
            )

    def test_context_type_is_validated(
        self,
    ):

        service = (
            MemoryDecisionService()
        )

        service.register_provider(
            FakeDecisionProvider()
        )

        with self.assertRaises(
            TypeError
        ):

            service.decide(
                "not a context"
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )