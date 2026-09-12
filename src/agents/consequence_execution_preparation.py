"""M33 bridge from consequence authorization into execution preparation.

M33 reuses the existing authorization-integrity, sandbox-admission, and
execution-preparation boundaries. It does not execute a tool or assign an
execution worker.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from src.tools.authorization_integrity import (
    AuthorizationIntegrityResult,
    AuthorizationIntegrityService,
)
from src.tools.execution_preparation import ExecutionHandoff, ExecutionPreparationService
from src.tools.models import ToolDefinition, ToolRequest
from src.tools.sandbox_admission import (
    SandboxAdmissionDecision,
    SandboxAdmissionService,
    build_default_sandbox_profiles,
)

from src.agents.consequence_authorization import (
    ConsequenceAuthorizationDecision,
    ConsequenceAuthorizationStatus,
)


class ConsequenceExecutionPreparationStatus(str, Enum):
    """Outcome of the M32 -> M33 preparation boundary."""

    PREPARED = "PREPARED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ConsequenceExecutionPreparation:
    """Immutable preparation result preserving the complete upstream lineage."""

    preparation_id: str
    authorization_id: str
    handoff_id: str
    claim_id: str
    task_id: str
    consequence_id: str
    tool_name: str
    invocation_id: str | None
    status: ConsequenceExecutionPreparationStatus
    authorization_granted: bool
    evidence_refs: tuple[str, ...]
    verification_refs: tuple[str, ...]
    integrity: AuthorizationIntegrityResult | None
    sandbox_admission: SandboxAdmissionDecision | None
    execution_handoff: ExecutionHandoff | None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("preparation_id", self.preparation_id),
            ("authorization_id", self.authorization_id),
            ("handoff_id", self.handoff_id),
            ("claim_id", self.claim_id),
            ("task_id", self.task_id),
            ("consequence_id", self.consequence_id),
            ("tool_name", self.tool_name),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if self.invocation_id is not None and not isinstance(self.invocation_id, str):
            raise TypeError("invocation_id must be a string or None")
        if not isinstance(self.status, ConsequenceExecutionPreparationStatus):
            raise TypeError("status must be a ConsequenceExecutionPreparationStatus member")
        if not isinstance(self.authorization_granted, bool):
            raise TypeError("authorization_granted must be a bool")
        if any(not isinstance(ref, str) or not ref for ref in self.evidence_refs):
            raise TypeError("evidence_refs must contain non-empty strings")
        if any(not isinstance(ref, str) or not ref for ref in self.verification_refs):
            raise TypeError("verification_refs must contain non-empty strings")
        if self.integrity is not None and not isinstance(
            self.integrity, AuthorizationIntegrityResult
        ):
            raise TypeError("integrity must be an AuthorizationIntegrityResult or None")
        if self.sandbox_admission is not None and not isinstance(
            self.sandbox_admission, SandboxAdmissionDecision
        ):
            raise TypeError("sandbox_admission must be a SandboxAdmissionDecision or None")
        if self.execution_handoff is not None and not isinstance(
            self.execution_handoff, ExecutionHandoff
        ):
            raise TypeError("execution_handoff must be an ExecutionHandoff or None")
        if self.reason is not None and not isinstance(self.reason, str):
            raise TypeError("reason must be a string or None")

        if self.status is ConsequenceExecutionPreparationStatus.PREPARED:
            if not self.authorization_granted:
                raise ValueError("PREPARED requires granted authorization")
            if self.integrity is None or not self.integrity.valid:
                raise ValueError("PREPARED requires valid authorization integrity")
            if self.sandbox_admission is None or not self.sandbox_admission.admissible:
                raise ValueError("PREPARED requires admissible sandbox admission")
            if self.execution_handoff is None:
                raise ValueError("PREPARED requires an execution handoff")
            if self.reason is not None:
                raise ValueError("PREPARED cannot contain a blocking reason")
        elif self.status is ConsequenceExecutionPreparationStatus.BLOCKED:
            if self.execution_handoff is not None:
                raise ValueError("BLOCKED cannot contain an execution handoff")
            if self.reason is None or not self.reason.strip():
                raise ValueError("BLOCKED requires a reason")

    @property
    def prepared(self) -> bool:
        return self.status is ConsequenceExecutionPreparationStatus.PREPARED

    def to_context(self) -> dict[str, object]:
        return {
            "preparation_id": self.preparation_id,
            "authorization_id": self.authorization_id,
            "authority_handoff_id": self.handoff_id,
            "claim_id": self.claim_id,
            "task_id": self.task_id,
            "consequence_id": self.consequence_id,
            "tool_name": self.tool_name,
            "invocation_id": self.invocation_id,
            "execution_preparation_status": self.status.value,
            "execution_prepared": self.prepared,
            "execution_started": False,
            "worker_assigned": False,
            "containment_active": False,
            "authorization_granted": self.authorization_granted,
            "evidence_refs": self.evidence_refs,
            "verification_refs": self.verification_refs,
            "execution_handoff_id": (
                self.execution_handoff.handoff_id if self.execution_handoff is not None else None
            ),
            "reason": self.reason,
        }


class ConsequenceExecutionPreparationService:
    """Prepare an authorized consequence through the existing execution walls."""

    def __init__(
        self,
        integrity_service: AuthorizationIntegrityService | None = None,
        sandbox_admission_service: SandboxAdmissionService | None = None,
        execution_preparation_service: ExecutionPreparationService | None = None,
    ) -> None:
        self._integrity = integrity_service or AuthorizationIntegrityService()
        self._sandbox = sandbox_admission_service or SandboxAdmissionService(
            build_default_sandbox_profiles()
        )
        self._preparation = execution_preparation_service or ExecutionPreparationService()

        if not isinstance(self._integrity, AuthorizationIntegrityService):
            raise TypeError("integrity_service must be an AuthorizationIntegrityService")
        if not isinstance(self._sandbox, SandboxAdmissionService):
            raise TypeError("sandbox_admission_service must be a SandboxAdmissionService")
        if not isinstance(self._preparation, ExecutionPreparationService):
            raise TypeError(
                "execution_preparation_service must be an ExecutionPreparationService"
            )

    def prepare(
        self,
        authorization: ConsequenceAuthorizationDecision,
        definition: ToolDefinition,
        request: ToolRequest,
    ) -> ConsequenceExecutionPreparation:
        if not isinstance(authorization, ConsequenceAuthorizationDecision):
            raise TypeError("authorization must be a ConsequenceAuthorizationDecision")
        if not isinstance(definition, ToolDefinition):
            raise TypeError("definition must be a ToolDefinition")
        if not isinstance(request, ToolRequest):
            raise TypeError("request must be a ToolRequest")

        if authorization.status is not ConsequenceAuthorizationStatus.AUTHORIZED:
            return self._blocked(authorization, request, "consequence authorization is not granted", authorization_granted=False)

        underlying = authorization.underlying_decision
        if underlying is None or not underlying.authorized:
            return self._blocked(
                authorization,
                request,
                "authorized consequence is missing an authorized underlying decision",
                authorization_granted=False,
            )

        if definition.name.strip().lower() != request.tool_name.strip().lower():
            return self._blocked(
                authorization,
                request,
                "tool definition identity does not match request",
                authorization_granted=True,
            )
        if underlying.authorization_id != authorization.authorization_id:
            return self._blocked(
                authorization,
                request,
                "underlying authorization identity does not match consequence authorization",
                authorization_granted=True,
            )
        if underlying.tool_name.strip().lower() != request.tool_name.strip().lower():
            return self._blocked(
                authorization,
                request,
                "underlying authorization tool identity does not match request",
                authorization_granted=True,
            )
        if underlying.invocation_id != request.invocation_id:
            return self._blocked(
                authorization,
                request,
                "underlying authorization invocation identity does not match request",
                authorization_granted=True,
            )

        integrity = self._integrity.attest(underlying, request)
        if not self._integrity.verify(integrity, underlying, request):
            return self._blocked(
                authorization,
                request,
                integrity.reason or "authorization integrity verification failed",
                authorization_granted=True,
                integrity=integrity,
            )

        profile_id = definition.metadata.get("sandbox_profile_id")
        admission = self._sandbox.admit(
            underlying,
            integrity,
            request,
            profile_id=profile_id,
        )
        if not admission.admissible:
            return self._blocked(
                authorization,
                request,
                admission.reason or "sandbox admission failed",
                authorization_granted=True,
                integrity=integrity,
                sandbox_admission=admission,
            )

        execution_handoff = self._preparation.prepare(
            underlying,
            integrity,
            admission,
            request,
        )
        preparation_id = self._preparation_id(authorization, execution_handoff)
        return ConsequenceExecutionPreparation(
            preparation_id=preparation_id,
            authorization_id=authorization.authorization_id,
            handoff_id=authorization.handoff_id,
            claim_id=authorization.claim_id,
            task_id=authorization.task_id,
            consequence_id=authorization.consequence_id,
            tool_name=authorization.tool_name,
            invocation_id=authorization.invocation_id,
            status=ConsequenceExecutionPreparationStatus.PREPARED,
            authorization_granted=True,
            evidence_refs=authorization.evidence_refs,
            verification_refs=authorization.verification_refs,
            integrity=integrity,
            sandbox_admission=admission,
            execution_handoff=execution_handoff,
        )

    @staticmethod
    def _blocked(
        authorization: ConsequenceAuthorizationDecision,
        request: ToolRequest,
        reason: str,
        *,
        authorization_granted: bool,
        integrity: AuthorizationIntegrityResult | None = None,
        sandbox_admission: SandboxAdmissionDecision | None = None,
    ) -> ConsequenceExecutionPreparation:
        return ConsequenceExecutionPreparation(
            preparation_id=ConsequenceExecutionPreparationService._blocked_id(
                authorization,
                request,
                reason,
            ),
            authorization_id=authorization.authorization_id,
            handoff_id=authorization.handoff_id,
            claim_id=authorization.claim_id,
            task_id=authorization.task_id,
            consequence_id=authorization.consequence_id,
            tool_name=request.tool_name,
            invocation_id=request.invocation_id,
            status=ConsequenceExecutionPreparationStatus.BLOCKED,
            authorization_granted=authorization_granted,
            evidence_refs=authorization.evidence_refs,
            verification_refs=authorization.verification_refs,
            integrity=integrity,
            sandbox_admission=sandbox_admission,
            execution_handoff=None,
            reason=reason,
        )

    @staticmethod
    def _preparation_id(
        authorization: ConsequenceAuthorizationDecision,
        execution_handoff: ExecutionHandoff,
    ) -> str:
        payload = json.dumps(
            {
                "authorization_id": authorization.authorization_id,
                "handoff_id": authorization.handoff_id,
                "claim_id": authorization.claim_id,
                "task_id": authorization.task_id,
                "consequence_id": authorization.consequence_id,
                "execution_handoff_id": execution_handoff.handoff_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"prep-{hashlib.sha256(payload).hexdigest()[:24]}"

    @staticmethod
    def _blocked_id(
        authorization: ConsequenceAuthorizationDecision,
        request: ToolRequest,
        reason: str,
    ) -> str:
        payload = json.dumps(
            {
                "authorization_id": authorization.authorization_id,
                "handoff_id": authorization.handoff_id,
                "tool_name": request.tool_name.strip().lower(),
                "invocation_id": request.invocation_id,
                "reason": reason,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return f"prep-{hashlib.sha256(payload).hexdigest()[:24]}"


__all__ = [
    "ConsequenceExecutionPreparation",
    "ConsequenceExecutionPreparationService",
    "ConsequenceExecutionPreparationStatus",
]
