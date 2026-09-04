"""M16.1 controlled self-development proposal boundary.

A SelfDevelopmentProposal describes a possible change to JARVIS itself. It is
not an instruction, authorization, policy decision, execution request, or
permission to modify the system.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


class SelfDevelopmentValidationError(ValueError):
    """Raised when a self-development proposal violates the M16.1 boundary."""


MAX_ID_LENGTH = 256
MAX_TITLE_LENGTH = 512
MAX_DESCRIPTION_LENGTH = 2048
MAX_TARGET_LENGTH = 1024
MAX_LIST_ITEMS = 64
MAX_ITEM_LENGTH = 512
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SelfDevelopmentValidationError(
            f"{field_name} must be a non-empty string"
        )
    if len(value) > maximum:
        raise SelfDevelopmentValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise SelfDevelopmentValidationError(
                f"{path} contains a non-finite number"
            )
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise SelfDevelopmentValidationError(
                    f"{path} keys must be non-empty strings"
                )
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise SelfDevelopmentValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _text_tuple(values: tuple[str, ...], field_name: str) -> None:
    if not isinstance(values, tuple):
        raise SelfDevelopmentValidationError(f"{field_name} must be a tuple")
    if len(values) > MAX_LIST_ITEMS:
        raise SelfDevelopmentValidationError(
            f"{field_name} exceeds maximum count of {MAX_LIST_ITEMS}"
        )
    if len(set(values)) != len(values):
        raise SelfDevelopmentValidationError(f"{field_name} must be unique")
    for index, value in enumerate(values):
        _text(value, f"{field_name}[{index}]", MAX_ITEM_LENGTH)


@dataclass(frozen=True)
class SelfDevelopmentProposal:
    """Immutable bounded proposal for a possible JARVIS self-change."""

    proposal_id: str
    title: str
    description: str
    target: str
    rationale: str
    expected_change: str
    affected_paths: tuple[str, ...] = ()
    validation_requirements: tuple[str, ...] = ()
    rollback_plan: str = ""
    reversible: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.proposal_id, "proposal_id", MAX_ID_LENGTH)
        _text(self.title, "title", MAX_TITLE_LENGTH)
        _text(self.description, "description", MAX_DESCRIPTION_LENGTH)
        _text(self.target, "target", MAX_TARGET_LENGTH)
        _text(self.rationale, "rationale", MAX_DESCRIPTION_LENGTH)
        _text(self.expected_change, "expected_change", MAX_DESCRIPTION_LENGTH)
        _text_tuple(self.affected_paths, "affected_paths")
        _text_tuple(self.validation_requirements, "validation_requirements")
        if not isinstance(self.rollback_plan, str):
            raise SelfDevelopmentValidationError("rollback_plan must be a string")
        if len(self.rollback_plan) > MAX_DESCRIPTION_LENGTH:
            raise SelfDevelopmentValidationError(
                f"rollback_plan exceeds maximum length of {MAX_DESCRIPTION_LENGTH}"
            )
        if not isinstance(self.reversible, bool):
            raise SelfDevelopmentValidationError("reversible must be a bool")
        if self.reversible and not self.rollback_plan.strip():
            raise SelfDevelopmentValidationError(
                "reversible proposals require a rollback_plan"
            )
        if not isinstance(self.metadata, Mapping):
            raise SelfDevelopmentValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise SelfDevelopmentValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def with_affected_path(self, path: str) -> "SelfDevelopmentProposal":
        _text(path, "path", MAX_ITEM_LENGTH)
        if path in self.affected_paths:
            raise SelfDevelopmentValidationError("affected path already exists")
        return SelfDevelopmentProposal(
            proposal_id=self.proposal_id,
            title=self.title,
            description=self.description,
            target=self.target,
            rationale=self.rationale,
            expected_change=self.expected_change,
            affected_paths=self.affected_paths + (path,),
            validation_requirements=self.validation_requirements,
            rollback_plan=self.rollback_plan,
            reversible=self.reversible,
            metadata=self.metadata,
        )

    def with_validation_requirement(self, requirement: str) -> "SelfDevelopmentProposal":
        _text(requirement, "requirement", MAX_ITEM_LENGTH)
        if requirement in self.validation_requirements:
            raise SelfDevelopmentValidationError(
                "validation requirement already exists"
            )
        return SelfDevelopmentProposal(
            proposal_id=self.proposal_id,
            title=self.title,
            description=self.description,
            target=self.target,
            rationale=self.rationale,
            expected_change=self.expected_change,
            affected_paths=self.affected_paths,
            validation_requirements=self.validation_requirements + (requirement,),
            rollback_plan=self.rollback_plan,
            reversible=self.reversible,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "target": self.target,
            "rationale": self.rationale,
            "expected_change": self.expected_change,
            "affected_paths": list(self.affected_paths),
            "validation_requirements": list(self.validation_requirements),
            "rollback_plan": self.rollback_plan,
            "reversible": self.reversible,
            "metadata": _thaw(self.metadata),
            "self_change_proposed": True,
            "instruction_granted": False,
            "authorization_granted": False,
            "policy_authority": False,
            "confirmation_granted": False,
            "execution_requested": False,
            "authority_scope_change": False,
            "identity_change_authorized": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
