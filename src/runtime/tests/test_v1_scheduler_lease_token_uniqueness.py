import unittest

from src.runtime.autonomous_runtime_scheduler import scheduler_claim_token


class V1SchedulerLeaseTokenUniquenessTests(unittest.TestCase):
    def test_identical_claim_inputs_produce_distinct_tokens(self):
        first = scheduler_claim_token("job-1", 40.0, 30.0)
        second = scheduler_claim_token("job-1", 40.0, 30.0)
        self.assertNotEqual(first, second)
        self.assertTrue(first.startswith("scheduler-claim-"))
        self.assertTrue(second.startswith("scheduler-claim-"))


if __name__ == "__main__":
    unittest.main()
