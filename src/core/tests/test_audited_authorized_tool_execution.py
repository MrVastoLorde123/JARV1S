import tempfile
import unittest
from pathlib import Path

from src.core.audited_authorized_tool_execution import AuditedAuthorizedToolPlanStepHandler
from src.core.execution_plan_models import PlanStep
from src.core.tool_authorization_evidence_store import ToolAuthorizationEvidenceStore
from src.core.tool_authorization_policy import (
    StaticToolAuthorizationPolicy,
    ToolAuthorizationPolicyRule,
)
from src.core.tool_execution import ToolExecutionConfirmation
from src.tools.models import ToolError, ToolResult
from src.tools.protocol import ToolHandler


class RecordingHandler(ToolHandler):
    def __init__(self) -> None:
        self.calls = []
        self._definition = self._build_definition()

    @staticmethod
    def _build_definition():
        from src.tools.models import RiskLevel, ToolDefinition

        return ToolDefinition(
            name="ping_host",
            description="Ping a host",
            version="1",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
        )

    def definition(self):
        return self._definition

    def execute(self, request):
        self.calls.append(request)
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={"ok": True},
            invocation_id=request.invocation_id,
        )


class FailingEvidenceStore(ToolAuthorizationEvidenceStore):
    def save(self, evidence):
        raise RuntimeError("evidence persistence unavailable")


class AuditedAuthorizedToolExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "authorization.db"
        self.store = ToolAuthorizationEvidenceStore(self.database_path)
        self.handler = RecordingHandler()
        self.step = PlanStep(
            step_id="step-1",
            description="Run diagnostic",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "ping_host",
                "arguments": {"host": "127.0.0.1"},
            },
        )
        self.policy = StaticToolAuthorizationPolicy(
            (
                ToolAuthorizationPolicyRule(
                    policy_id="ops-read",
                    scope="diagnostics",
                    allowed_capability_classes=("diagnostic",),
                    allowed_tools=("ping_host",),
                ),
            )
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _step_with_policy_metadata(self) -> PlanStep:
        metadata = dict(self.step.metadata)
        metadata["scope"] = "diagnostics"
        metadata["capability_class"] = "diagnostic"
        return PlanStep(
            step_id=self.step.step_id,
            description=self.step.description,
            action=self.step.action,
            order=self.step.order,
            depends_on=self.step.depends_on,
            status=self.step.status,
            requires_confirmation=self.step.requires_confirmation,
            metadata=metadata,
        )

    def _adapter(self, store=None, policy=None):
        from src.core.tool_execution import ToolInvoker

        class Invoker(ToolInvoker):
            def __init__(self, handler):
                self.handler = handler

            def invoke(self, request):
                return self.handler.execute(request)

        return AuditedAuthorizedToolPlanStepHandler(
            Invoker(self.handler),
            policy or self.policy,
            store or self.store,
        )

    def test_authorized_execution_persists_before_invocation(self) -> None:
        adapter = self._adapter()
        result = adapter(self._step_with_policy_metadata())
        self.assertTrue(result["ok"])
        self.assertEqual(len(self.handler.calls), 1)
        evidence = self.store.all()
        self.assertEqual(len(evidence), 1)
        self.assertTrue(evidence[0].evidence.authorized)

    def test_denied_authorization_is_persisted_but_never_executes(self) -> None:
        denied_policy = StaticToolAuthorizationPolicy(
            (
                ToolAuthorizationPolicyRule(
                    policy_id="ops-read",
                    scope="diagnostics",
                    allowed_capability_classes=("diagnostic",),
                    allowed_tools=("read_status",),
                ),
            )
        )
        adapter = self._adapter(policy=denied_policy)
        with self.assertRaises(PermissionError):
            adapter(self._step_with_policy_metadata())
        self.assertEqual(self.handler.calls, [])
        evidence = self.store.all()
        self.assertEqual(len(evidence), 1)
        self.assertFalse(evidence[0].evidence.authorized)

    def test_persistence_failure_prevents_execution(self) -> None:
        adapter = self._adapter(store=FailingEvidenceStore(self.database_path))
        with self.assertRaises(RuntimeError):
            adapter(self._step_with_policy_metadata())
        self.assertEqual(self.handler.calls, [])

    def test_required_confirmation_remains_separate(self) -> None:
        confirmed_step = self._step_with_policy_metadata()
        confirmed_step = PlanStep(
            step_id=confirmed_step.step_id,
            description=confirmed_step.description,
            action=confirmed_step.action,
            order=confirmed_step.order,
            depends_on=confirmed_step.depends_on,
            status=confirmed_step.status,
            requires_confirmation=True,
            metadata=confirmed_step.metadata,
        )
        adapter = self._adapter()
        with self.assertRaises(PermissionError):
            adapter(confirmed_step)
        self.assertEqual(self.handler.calls, [])
        self.assertEqual(len(self.store.all()), 1)
        self.assertTrue(self.store.all()[0].evidence.authorized)

    def test_exact_confirmation_allows_execution_after_persistence(self) -> None:
        confirmed_step = self._step_with_policy_metadata()
        confirmed_step = PlanStep(
            step_id=confirmed_step.step_id,
            description=confirmed_step.description,
            action=confirmed_step.action,
            order=confirmed_step.order,
            depends_on=confirmed_step.depends_on,
            status=confirmed_step.status,
            requires_confirmation=True,
            metadata=confirmed_step.metadata,
        )
        from src.core.tool_execution import ToolPlanStepHandler

        request = ToolPlanStepHandler.build_request(confirmed_step)
        confirmation = ToolExecutionConfirmation(
            step_id=confirmed_step.step_id,
            request=request,
            confirmed=True,
        )
        result = self._adapter()(confirmed_step, confirmation)
        self.assertEqual(result, {"ok": True})
        self.assertEqual(len(self.handler.calls), 1)


if __name__ == "__main__":
    unittest.main()
