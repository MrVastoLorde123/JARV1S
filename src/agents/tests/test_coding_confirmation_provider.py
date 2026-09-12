from __future__ import annotations

import unittest

from src.agents.coding_confirmation import CodingAgentConfirmationService
from src.agents.coding_confirmation_provider import CodingAgentConfirmationProvider
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentTask,
    CodingAgentVerification,
)
from src.tools.models import ToolRequest, ToolDefinition, RiskLevel


class M28CodingAgentConfirmationProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CodingAgentConfirmationService()
        self.provider = CodingAgentConfirmationProvider(self.service)
        self.task = CodingAgentTask(objective="Update the interface", task_id="coding-provider-001")
        self.plan = CodingAgentPlan(
            edits=(CodingAgentEdit(path="ui/src/App.tsx", content="approved", overwrite=True),),
            verification=CodingAgentVerification(runner="npm_build"),
        )
        self.operation = self.service.stage(self.task, self.plan)
        self.service.confirm(self.operation.operation_id)
        self.definition = ToolDefinition(
            name="write_file",
            description="write a file",
            risk_level=RiskLevel.HIGH,
            requires_confirmation=True,
        )

    def _request(self, **overrides):
        values = {
            "tool_name": "write_file",
            "arguments": {
                "path": "ui/src/App.tsx",
                "content": "approved",
                "overwrite": True,
                "create_parents": False,
            },
            "metadata": {
                "coding_operation_id": self.operation.operation_id,
                "task_id": self.task.task_id,
                "edit_index": 0,
            },
            "invocation_id": "coding-provider-001-edit-1",
        }
        values.update(overrides)
        return ToolRequest(**values)

    def test_approved_exact_request_is_confirmed(self) -> None:
        response = self.provider.confirm(self.definition, self._request())
        self.assertTrue(response.approved)

    def test_unconfirmed_operation_is_rejected(self) -> None:
        service = CodingAgentConfirmationService()
        operation = service.stage(self.task, self.plan)
        provider = CodingAgentConfirmationProvider(service)
        request = self._request(
            metadata={
                "coding_operation_id": operation.operation_id,
                "task_id": self.task.task_id,
                "edit_index": 0,
            }
        )
        response = provider.confirm(self.definition, request)
        self.assertFalse(response.approved)

    def test_modified_content_is_rejected(self) -> None:
        request = self._request(
            arguments={
                "path": "ui/src/App.tsx",
                "content": "NOT APPROVED",
                "overwrite": True,
                "create_parents": False,
            }
        )
        response = self.provider.confirm(self.definition, request)
        self.assertFalse(response.approved)

    def test_replay_of_same_invocation_is_rejected(self) -> None:
        request = self._request()
        first = self.provider.confirm(self.definition, request)
        second = self.provider.confirm(self.definition, request)
        self.assertTrue(first.approved)
        self.assertFalse(second.approved)


if __name__ == "__main__":
    unittest.main()
