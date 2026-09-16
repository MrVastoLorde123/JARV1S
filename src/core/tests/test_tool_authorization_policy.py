import json
import unittest

from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization
from src.core.tool_authorization_policy import (
    StaticToolAuthorizationPolicy,
    ToolAuthorizationEvidence,
    ToolAuthorizationPolicyRule,
)
from src.tools.models import ToolRequest


class ToolAuthorizationPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.step = PlanStep(
            step_id="step-1",
            description="Run a diagnostic tool",
            action="USE_TOOL",
            order=0,
        )
        self.rule = ToolAuthorizationPolicyRule(
            policy_id="ops-read",
            scope="diagnostics",
            allowed_capability_classes=("diagnostic",),
            allowed_tools=("ping_host", "read_status"),
        )
        self.policy = StaticToolAuthorizationPolicy((self.rule,))

    def _request(
        self,
        *,
        tool_name="ping_host",
        scope="diagnostics",
        capability_class="diagnostic",
        invocation_id="inv-1",
    ) -> ToolRequest:
        return ToolRequest(
            tool_name=tool_name,
            metadata={
                "scope": scope,
                "capability_class": capability_class,
            },
            invocation_id=invocation_id,
        )

    def test_rule_is_immutable_and_normalizes_values(self) -> None:
        self.assertEqual(self.rule.scope, "diagnostics")
        self.assertEqual(self.rule.allowed_capability_classes, ("diagnostic",))
        with self.assertRaises((AttributeError, TypeError)):
            self.rule.scope = "other"  # type: ignore[misc]

    def test_policy_requires_at_least_one_rule(self) -> None:
        with self.assertRaises(ValueError):
            StaticToolAuthorizationPolicy(())

    def test_policy_rejects_duplicate_policy_ids(self) -> None:
        duplicate = ToolAuthorizationPolicyRule(
            policy_id="ops-read",
            scope="other",
        )
        with self.assertRaises(ValueError):
            StaticToolAuthorizationPolicy((self.rule, duplicate))

    def test_matching_scope_class_and_tool_are_authorized(self) -> None:
        authorization = self.policy.authorize(self.step, self._request())
        self.assertTrue(authorization.authorized)
        self.assertEqual(authorization.policy_id, "ops-read")
        self.assertEqual(authorization.request.tool_name, "ping_host")

    def test_non_matching_scope_is_denied(self) -> None:
        authorization = self.policy.authorize(
            self.step,
            self._request(scope="production"),
        )
        self.assertFalse(authorization.authorized)
        self.assertEqual(authorization.policy_id, "no-matching-policy")

    def test_missing_capability_class_is_denied(self) -> None:
        request = self._request(capability_class=None)
        authorization = self.policy.authorize(self.step, request)
        self.assertFalse(authorization.authorized)
        self.assertIn("capability_class", authorization.reason)

    def test_disallowed_capability_class_is_denied(self) -> None:
        authorization = self.policy.authorize(
            self.step,
            self._request(capability_class="write"),
        )
        self.assertFalse(authorization.authorized)
        self.assertIn("not allowed", authorization.reason)

    def test_disallowed_tool_is_denied(self) -> None:
        authorization = self.policy.authorize(
            self.step,
            self._request(tool_name="delete_everything"),
        )
        self.assertFalse(authorization.authorized)
        self.assertIn("not allowed", authorization.reason)

    def test_explicit_denial_overrides_allowance(self) -> None:
        policy = StaticToolAuthorizationPolicy(
            (
                ToolAuthorizationPolicyRule(
                    policy_id="ops-read",
                    scope="diagnostics",
                    allowed_capability_classes=("diagnostic",),
                    allowed_tools=("ping_host",),
                    denied_tools=("ping_host",),
                ),
            )
        )
        authorization = policy.authorize(self.step, self._request())
        self.assertFalse(authorization.authorized)
        self.assertIn("denied", authorization.reason)

    def test_explicit_capability_denial_overrides_allowance(self) -> None:
        policy = StaticToolAuthorizationPolicy(
            (
                ToolAuthorizationPolicyRule(
                    policy_id="ops-read",
                    scope="diagnostics",
                    allowed_capability_classes=("diagnostic",),
                    denied_capability_classes=("diagnostic",),
                ),
            )
        )
        authorization = policy.authorize(self.step, self._request())
        self.assertFalse(authorization.authorized)
        self.assertIn("denied", authorization.reason)

    def test_evidence_is_json_native_and_round_trips_fields(self) -> None:
        authorization = self.policy.authorize(self.step, self._request())
        evidence = ToolAuthorizationEvidence.from_authorization(authorization)
        record = evidence.to_record()
        self.assertEqual(record["step_id"], "step-1")
        self.assertEqual(record["invocation_id"], "inv-1")
        self.assertEqual(record["tool_name"], "ping_host")
        self.assertEqual(record["scope"], "diagnostics")
        self.assertEqual(record["capability_class"], "diagnostic")
        self.assertTrue(record["authorized"])
        self.assertEqual(json.loads(json.dumps(record)), record)
        record["authorized"] = False
        self.assertTrue(evidence.authorized)

    def test_evidence_requires_scope_and_capability_class(self) -> None:
        authorization = ToolExecutionAuthorization(
            step_id="step-1",
            request=ToolRequest(tool_name="ping_host", invocation_id="inv-1"),
            authorized=True,
            policy_id="ops-read",
            reason="authorized",
        )
        with self.assertRaises(ValueError):
            ToolAuthorizationEvidence.from_authorization(authorization)

    def test_evidence_is_not_an_execution_result(self) -> None:
        authorization = self.policy.authorize(self.step, self._request())
        evidence = ToolAuthorizationEvidence.from_authorization(authorization)
        self.assertFalse(hasattr(evidence, "success"))
        self.assertFalse(hasattr(evidence, "content"))


if __name__ == "__main__":
    unittest.main()
