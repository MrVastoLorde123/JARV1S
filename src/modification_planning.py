"""M16.3 controlled self-development modification planning boundary.

A ControlledModificationPlan turns a self-development proposal and its impact
assessment into an ordered, bounded plan. It describes how a change could be
validated and recovered; it does not authorize, execute, or approve the change.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.change_impact import ChangeImpactAssessment


class ModificationPlanValidationError(ValueError):
    """Raised when a modification plan violates the M16.3 boundary."""


class ModificationStepKind(str, Enum):
    """Descriptive kinds of work that may appear in a modification plan."""

    INSPECT = "inspect"
    PREPARE = "prepare"
    MODIFY = "modify"
    TEST = "test"
    OBSERVE = "observe"
    VERIFY = "verify"
    CHECKPOINT = "checkpoint"
    ROLLBACK = "rollback"


MAX_ID_LENGTH = 256
MAX_DESCRIPTION_LENGTH = 2048
MAX_ITEM_LENGTH = 512
MAX_LIST_ITEMS = 64
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModificationPlanValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise ModificationPlanValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _text_tuple(values: tuple[str, ...], field_name: str) -> None:
    if not isinstance(values, tuple):
        raise ModificationPlanValidationError(f"{field_name} must be a tuple")
    if len(values) > MAX_LIST_ITEMS:
        raise ModificationPlanValidationError(
            f"{field_name} exceeds maximum count of {MAX_LIST_ITEMS}"
        )
    if len(set(values)) != len(values):
        raise ModificationPlanValidationError(f"{field_name} must be unique")
    for index, value in enumerate(values):
        _text(value, f"{field_name}[{index}]", MAX_ITEM_LENGTH)


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if value != value or abs(value) == float("inf"):
            raise ModificationPlanValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ModificationPlanValidationError(
                    f"{path} keys must be non-empty strings"
                )
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise ModificationPlanValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class ModificationStep:
    """One ordered, descriptive step in a possible modification plan."""

    step_id: str
    kind: ModificationStepKind
    description: str
    validation_gate: str
    rollback_checkpoint: str = ""

    def __post_init__(self) -> None:
        _text(self.step_id, "step_id", MAX_ID_LENGTH)
        if not isinstance(self.kind, ModificationStepKind):
            raise ModificationPlanValidationError("kind must be a ModificationStepKind")
        _text(self.description, "description", MAX_DESCRIPTION_LENGTH)
        _text(self.validation_gate, "validation_gate", MAX_ITEM_LENGTH)
        if not isinstance(self.rollback_checkpoint, str):
            raise ModificationPlanValidationError("rollback_checkpoint must be a string")
        if len(self.rollback_checkpoint) > MAX_ITEM_LENGTH:
            raise ModificationPlanValidationError(
                f"rollback_checkpoint exceeds maximum length of {MAX_ITEM_LENGTH}"
            )


@dataclass(frozen=True)
class ControlledModificationPlan:
    """Immutable bounded plan for a possible self-development modification."""

    plan_id: str
    assessment: ChangeImpactAssessment
    steps: tuple[ModificationStep, ...]
    validation_gates: tuple[str, ...] = ()
    rollback_checkpoints: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.plan_id, "plan_id", MAX_ID_LENGTH)
        if not isinstance(self.assessment, ChangeImpactAssessment):
            raise ModificationPlanValidationError(
                "assessment must be a ChangeImpactAssessment"
            )
        if not isinstance(self.steps, tuple):
            raise ModificationPlanValidationError("steps must be a tuple")
        if not self.steps:
            raise ModificationPlanValidationError("steps must contain at least one step")
        if len(self.steps) > MAX_LIST_ITEMS:
            raise ModificationPlanValidationError(
                f"steps exceeds maximum count of {MAX_LIST_ITEMS}"
            )
        step_ids: set[str] = set()
        for index, step in enumerate(self.steps):
            if not isinstance(step, ModificationStep):
                raise ModificationPlanValidationError(
                    f"steps[{index}] must be a ModificationStep"
                )
            if step.step_id in step_ids:
                raise ModificationPlanValidationError("step ids must be unique")
            step_ids.add(step.step_id)
        _text_tuple(self.validation_gates, "validation_gates")
        _text_tuple(self.rollback_checkpoints, "rollback_checkpoints")
        _text_tuple(self.constraints, "constraints")
        if not isinstance(self.metadata, Mapping):
            raise ModificationPlanValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise ModificationPlanValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def proposal_id(self) -> str:
        """Stable lineage back to the original self-development proposal."""

        return self.assessment.proposal_id

    @property
    def assessment_id(self) -> str:
        """Stable lineage back to the M16.2 impact assessment."""

        return self.assessment.assessment_id

    @property
    def requires_authority_review(self) -> bool:
        """Carry forward the assessment's descriptive authority-review flag."""

        return self.assessment.requires_authority_review

    @property
    def execution_requested(self) -> bool:
        """Always false: a plan never requests execution."""

        return False

    @property
    def authorization_granted(self) -> bool:
        """Always false: planning never grants authorization."""

        return False

    def with_step(self, step: ModificationStep) -> "ControlledModificationPlan":
        if not isinstance(step, ModificationStep):
            raise ModificationPlanValidationError("step must be a ModificationStep")
        if step.step_id in {existing.step_id for existing in self.steps}:
            raise ModificationPlanValidationError("step id already exists")
        return ControlledModificationPlan(
            plan_id=self.plan_id,
            assessment=self.assessment,
            steps=self.steps + (step,),
            validation_gates=self.validation_gates,
            rollback_checkpoints=self.rollback_checkpoints,
            constraints=self.constraints,
            metadata=self.metadata,
        )

    def with_validation_gate(self, gate: str) -> "ControlledModificationPlan":
        _text(gate, "gate", MAX_ITEM_LENGTH)
        if gate in self.validation_gates:
            raise ModificationPlanValidationError("validation gate already exists")
        return ControlledModificationPlan(
            plan_id=self.plan_id,
            assessment=self.assessment,
            steps=self.steps,
            validation_gates=self.validation_gates + (gate,),
            rollback_checkpoints=self.rollback_checkpoints,
            constraints=self.constraints,
            metadata=self.metadata,
        )

    def with_rollback_checkpoint(self, checkpoint: str) -> "ControlledModificationPlan":
        _text(checkpoint, "checkpoint", MAX_ITEM_LENGTH)
        if checkpoint in self.rollback_checkpoints:
            raise ModificationPlanValidationError("rollback checkpoint already exists")
        return ControlledModificationPlan(
            plan_id=self.plan_id,
            assessment=self.assessment,
            steps=self.steps,
            validation_gates=self.validation_gates,
            rollback_checkpoints=self.rollback_checkpoints + (checkpoint,),
            constraints=self.constraints,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "proposal_id": self.proposal_id,
            "assessment_id": self.assessment_id,
            "steps": [
                {
                    "step_id": step.step_id,
                    "kind": step.kind.value,
                    "description": step.description,
                    "validation_gate": step.validation_gate,
                    "rollback_checkpoint": step.rollback_checkpoint,
                }
                for step in self.steps
            ],
            "validation_gates": list(self.validation_gates),
            "rollback_checkpoints": list(self.rollback_checkpoints),
            "constraints": list(self.constraints),
            "metadata": _thaw(self.metadata),
            "modification_plan": True,
            "requires_authority_review": self.requires_authority_review,
            "authorization_granted": False,
            "instruction_granted": False,
            "execution_requested": False,
            "policy_authority": False,
            "authority_scope_change_authorized": False,
            "identity_change_authorized": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
