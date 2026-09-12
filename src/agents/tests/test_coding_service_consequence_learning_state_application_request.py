import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_learning_state_application_request import ConsequenceLearningStateApplicationRequestService
from src.agents.consequence_learning_state_consumption import ConsequenceLearningStateConsumption


class DummyWorker:
    pass


def consumption():
    return ConsequenceLearningStateConsumption(
        consumption_id="consumption-1",
        request_id="request-1",
        record_id="record-1",
        source_verification_id="verification-1",
        payload={"decision_status": "LEARNING_ELIGIBLE"},
        consumed=True,
        reason="verified",
    )


class M43CodingServiceTests(unittest.TestCase):
    def service(self, application_service=None):
        return CodingAgentService(
            object(),
            DummyWorker(),
            consequence_learning_state_application_request_service=application_service,
        )

    def test_requires_explicit_application_request_binding(self):
        with self.assertRaisesRegex(RuntimeError, "not bound"):
            self.service().request_consequence_learning_state_application(consumption())

    def test_accepts_injected_application_request_service(self):
        result = self.service(ConsequenceLearningStateApplicationRequestService()).request_consequence_learning_state_application(consumption())
        self.assertTrue(result.application_request_id.startswith("consequence-learning-state-application-request-"))

    def test_bind_accepts_service(self):
        service = self.service()
        service.bind_consequence_learning_state_application_request(ConsequenceLearningStateApplicationRequestService())
        result = service.request_consequence_learning_state_application(consumption())
        self.assertEqual(result.record_id, "record-1")

    def test_bind_requires_service(self):
        service = self.service()
        with self.assertRaisesRegex(ValueError, "application_request_service is required"):
            service.bind_consequence_learning_state_application_request()

    def test_application_request_does_not_grant_authority(self):
        result = self.service(ConsequenceLearningStateApplicationRequestService()).request_consequence_learning_state_application(consumption())
        context = result.to_context()
        self.assertFalse(context["memory_mutated"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["retry_requested"])


if __name__ == "__main__":
    unittest.main()
