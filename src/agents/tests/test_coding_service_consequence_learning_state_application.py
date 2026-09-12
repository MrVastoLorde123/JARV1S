import unittest

from src.agents.coding_service import CodingAgentService
from src.agents.consequence_learning_state_application import ConsequenceLearningStateApplicationService
from src.agents.consequence_learning_state_application_request import ConsequenceLearningStateApplicationRequest


class DummyWorker:
    pass


class Applicator:
    def apply(self, *, application_request_id, request_id, record_id, payload):
        return "applied-record-1"


def request():
    return ConsequenceLearningStateApplicationRequest(
        application_request_id="application-request-1",
        consumption_id="consumption-1",
        request_id="request-1",
        record_id="record-1",
        verification_id="verification-1",
        payload={"decision_status": "LEARNING_ELIGIBLE"},
        reason="verified",
    )


class M44CodingServiceTests(unittest.TestCase):
    def service(self, application=None):
        return CodingAgentService(
            object(),
            DummyWorker(),
            consequence_learning_state_application_service=application,
        )

    def test_requires_explicit_application_binding(self):
        with self.assertRaisesRegex(RuntimeError, "application service is not bound"):
            self.service().apply_consequence_learning_state(request())

    def test_accepts_injected_application_service(self):
        result = self.service(ConsequenceLearningStateApplicationService(Applicator())).apply_consequence_learning_state(request())
        self.assertTrue(result.applied)

    def test_bind_accepts_applicator(self):
        service = self.service()
        service.bind_consequence_learning_state_application(Applicator())
        self.assertEqual(service.apply_consequence_learning_state(request()).applied_record_id, "applied-record-1")

    def test_bind_accepts_application_service(self):
        service = self.service()
        service.bind_consequence_learning_state_application(application_service=ConsequenceLearningStateApplicationService(Applicator()))
        self.assertTrue(service.apply_consequence_learning_state(request()).applied)

    def test_bind_rejects_both(self):
        service = self.service()
        with self.assertRaisesRegex(ValueError, "either applicator or application_service"):
            service.bind_consequence_learning_state_application(
                Applicator(),
                application_service=ConsequenceLearningStateApplicationService(Applicator()),
            )

    def test_bind_requires_one_argument(self):
        service = self.service()
        with self.assertRaisesRegex(ValueError, "applicator or application_service is required"):
            service.bind_consequence_learning_state_application()


if __name__ == "__main__":
    unittest.main()
