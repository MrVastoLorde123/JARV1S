import unittest

from src.core.authorized_tool_execution import AuthorizedToolPlanStepHandler
from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization import ToolExecutionAuthorization
from src.core.tool_execution import ToolExecutionConfirmation
from src.tools.models import ToolRequest, ToolResult


class FakeToolInvoker:
    def __init__(self):
        self.requests = []

    def invoke(self, request):
        self.requests.append(request)
        return ToolResult(success=True, tool_name=request.tool_name, content="ok")


class FakePolicy:
    def __init__(self, authorization_factory):
        self.authorization_factory = authorization_factory
        self.calls = []

    def authorize(self, step, request):
        self.calls.append((step, request))
        return self.authorization_factory(step, request)


def make_step(*, requires_confirmation=False, path="README.md"):
    return PlanStep(
        step_id="step-auth-1",
        description="Read README",
        action="USE_TOOL",
        order=0,
        requires_confirmation=requires_confirmation,
        metadata={"tool_name": "read_file", "arguments": {"path": path}},
    )


def allow(step, request):
    return ToolExecutionAuthorization(
        step_id=step.step_id,
        request=request,
        authorized=True,
        policy_id="test-policy",
        reason="test policy allows this exact request",
    )


class AuthorizedToolExecutionTests(unittest.TestCase):
    def test_authorization_artifact_is_frozen(self):
        step = make_step()
        request = ToolRequest(
            tool_name="read_file",
            arguments={"path": "README.md"},
            invocation_id=step.step_id,
        )
        authorization = allow(step, request)

        with self.assertRaises(AttributeError):
            authorization.authorized = False

    def test_policy_receives_exact_materialized_request(self):
        invoker = FakeToolInvoker()
        policy = FakePolicy(allow)
        handler = AuthorizedToolPlanStepHandler(invoker, policy)
        step = make_step()

        handler(step)

        self.assertEqual(1, len(policy.calls))
        policy_step, policy_request = policy.calls[0]
        self.assertIs(step, policy_step)
        self.assertIsInstance(policy_request, ToolRequest)
        self.assertEqual("read_file", policy_request.tool_name)
        self.assertEqual({"path": "README.md"}, policy_request.arguments)
        self.assertEqual(step.step_id, policy_request.invocation_id)

    def test_missing_authorization_is_rejected_before_invocation(self):
        invoker = FakeToolInvoker()
        policy = FakePolicy(lambda step, request: None)
        handler = AuthorizedToolPlanStepHandler(invoker, policy)

        with self.assertRaises(TypeError):
            handler(make_step())

        self.assertEqual([], invoker.requests)

    def test_denied_authorization_is_rejected_before_invocation(self):
        invoker = FakeToolInvoker()
        policy = FakePolicy(
            lambda step, request: ToolExecutionAuthorization(
                step_id=step.step_id,
                request=request,
                authorized=False,
                policy_id="deny-policy",
                reason="tool is not permitted",
            )
        )
        handler = AuthorizedToolPlanStepHandler(invoker, policy)

        with self.assertRaisesRegex(PermissionError, "tool is not permitted"):
            handler(make_step())

        self.assertEqual([], invoker.requests)

    def test_mismatched_authorization_is_rejected_before_invocation(self):
        invoker = FakeToolInvoker()

        def stale(step, request):
            return ToolExecutionAuthorization(
                step_id="different-step",
                request=ToolRequest(
                    tool_name="read_file",
                    arguments={"path": "OTHER.md"},
                    invocation_id="different-step",
                ),
                authorized=True,
                policy_id="stale-policy",
                reason="stale decision",
            )

        handler = AuthorizedToolPlanStepHandler(invoker, FakePolicy(stale))

        with self.assertRaises(PermissionError):
            handler(make_step())

        self.assertEqual([], invoker.requests)

    def test_authorized_execution_reaches_invoker_once(self):
        invoker = FakeToolInvoker()
        handler = AuthorizedToolPlanStepHandler(invoker, FakePolicy(allow))

        self.assertEqual("ok", handler(make_step()))
        self.assertEqual(1, len(invoker.requests))
        self.assertEqual("read_file", invoker.requests[0].tool_name)

    def test_authorization_does_not_satisfy_required_confirmation(self):
        invoker = FakeToolInvoker()
        handler = AuthorizedToolPlanStepHandler(
            invoker,
            FakePolicy(allow),
        )
        step = make_step(requires_confirmation=True)

        with self.assertRaises(PermissionError):
            handler(step)

        self.assertEqual([], invoker.requests)

    def test_authorized_and_confirmed_execution_requires_both_artifacts(self):
        invoker = FakeToolInvoker()
        handler = AuthorizedToolPlanStepHandler(invoker, FakePolicy(allow))
        step = make_step(requires_confirmation=True)
        request = ToolRequest(
            tool_name="read_file",
            arguments={"path": "README.md"},
            invocation_id=step.step_id,
        )
        confirmation = ToolExecutionConfirmation(
            step_id=step.step_id,
            request=request,
        )

        self.assertEqual("ok", handler(step, confirmation))
        self.assertEqual([request], invoker.requests)

    def test_confirmation_must_still_match_when_authorized(self):
        invoker = FakeToolInvoker()
        handler = AuthorizedToolPlanStepHandler(invoker, FakePolicy(allow))
        step = make_step(requires_confirmation=True)
        stale_confirmation = ToolExecutionConfirmation(
            step_id=step.step_id,
            request=ToolRequest(
                tool_name="read_file",
                arguments={"path": "OTHER.md"},
                invocation_id=step.step_id,
            ),
        )

        with self.assertRaises(PermissionError):
            handler(step, stale_confirmation)

        self.assertEqual([], invoker.requests)

    def test_policy_can_be_injected_without_entering_planner_or_realization(self):
        invoker = FakeToolInvoker()
        calls = []

        def authorize(step, request):
            calls.append((step, request))
            return allow(step, request)

        handler = AuthorizedToolPlanStepHandler(invoker, FakePolicy(authorize))
        handler(make_step())

        self.assertEqual(1, len(calls))
        self.assertIs(invoker.requests[0], calls[0][1])


if __name__ == "__main__":
    unittest.main()
