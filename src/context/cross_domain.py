"""M14.5 cross-domain context boundary.

CrossDomainContext composes existing context domains and explicit descriptive
links between domain references. It does not infer authority, truth, intent,
priority, or permission from those links.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .goal_project import GoalProjectContext
from .situational import SituationalContext
from .world_state import ContextState


class CrossDomainContextValidationError(ValueError):
    """Raised when cross-domain context violates the M14.5 boundary."""


MAX_DOMAINS = 32
MAX_REFERENCES = 256
MAX_LINKS = 256
MAX_ID_LENGTH = 256
MAX_LABEL_LENGTH = 256
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CrossDomainContextValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise CrossDomainContextValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise CrossDomainContextValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise CrossDomainContextValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise CrossDomainContextValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class DomainReference:
    """Immutable reference to a known object in a named context domain."""

    domain: str
    reference_id: str
    label: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.domain, "domain", MAX_LABEL_LENGTH)
        _text(self.reference_id, "reference_id", MAX_ID_LENGTH)
        if self.label is not None:
            _text(self.label, "label", MAX_LABEL_LENGTH)
        if not isinstance(self.metadata, Mapping):
            raise CrossDomainContextValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise CrossDomainContextValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "reference_id": self.reference_id,
            "label": self.label,
            "metadata": _thaw(self.metadata),
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class CrossDomainLink:
    """Immutable descriptive link between two domain references."""

    source: DomainReference
    target: DomainReference
    relation: str
    source_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.source, DomainReference):
            raise CrossDomainContextValidationError("source must be a DomainReference")
        if not isinstance(self.target, DomainReference):
            raise CrossDomainContextValidationError("target must be a DomainReference")
        _text(self.relation, "relation", MAX_LABEL_LENGTH)
        if not isinstance(self.source_refs, tuple):
            raise CrossDomainContextValidationError("source_refs must be a tuple")
        if len(self.source_refs) > MAX_REFERENCES:
            raise CrossDomainContextValidationError(
                f"source_refs exceeds maximum count of {MAX_REFERENCES}"
            )
        if len(set(self.source_refs)) != len(self.source_refs):
            raise CrossDomainContextValidationError("source_refs must be unique")
        for index, ref in enumerate(self.source_refs):
            _text(ref, f"source_refs[{index}]", MAX_ID_LENGTH)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
            "relation": self.relation,
            "source_refs": list(self.source_refs),
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class CrossDomainContext:
    """Immutable bounded composition of multiple context domains."""

    context_state: ContextState | None = None
    goal_project: GoalProjectContext | None = None
    situational: SituationalContext | None = None
    references: tuple[DomainReference, ...] = ()
    links: tuple[CrossDomainLink, ...] = ()

    def __post_init__(self) -> None:
        if self.context_state is not None and not isinstance(self.context_state, ContextState):
            raise CrossDomainContextValidationError("context_state must be ContextState or None")
        if self.goal_project is not None and not isinstance(self.goal_project, GoalProjectContext):
            raise CrossDomainContextValidationError("goal_project must be GoalProjectContext or None")
        if self.situational is not None and not isinstance(self.situational, SituationalContext):
            raise CrossDomainContextValidationError("situational must be SituationalContext or None")
        if not isinstance(self.references, tuple):
            raise CrossDomainContextValidationError("references must be a tuple")
        if len(self.references) > MAX_REFERENCES:
            raise CrossDomainContextValidationError(
                f"references exceeds maximum count of {MAX_REFERENCES}"
            )
        if any(not isinstance(item, DomainReference) for item in self.references):
            raise CrossDomainContextValidationError("references must contain DomainReference values")
        keys = tuple((item.domain.casefold(), item.reference_id) for item in self.references)
        if len(set(keys)) != len(keys):
            raise CrossDomainContextValidationError("domain/reference pairs must be unique")
        if len({item.domain.casefold() for item in self.references}) > MAX_DOMAINS:
            raise CrossDomainContextValidationError(
                f"references exceed maximum domain count of {MAX_DOMAINS}"
            )
        if not isinstance(self.links, tuple):
            raise CrossDomainContextValidationError("links must be a tuple")
        if len(self.links) > MAX_LINKS:
            raise CrossDomainContextValidationError(
                f"links exceeds maximum count of {MAX_LINKS}"
            )
        if any(not isinstance(item, CrossDomainLink) for item in self.links):
            raise CrossDomainContextValidationError("links must contain CrossDomainLink values")
        reference_keys = set(keys)
        for link in self.links:
            if (link.source.domain.casefold(), link.source.reference_id) not in reference_keys:
                raise CrossDomainContextValidationError("link source must exist in references")
            if (link.target.domain.casefold(), link.target.reference_id) not in reference_keys:
                raise CrossDomainContextValidationError("link target must exist in references")

    def references_for_domain(self, domain: str) -> tuple[DomainReference, ...]:
        _text(domain, "domain", MAX_LABEL_LENGTH)
        normalized = domain.casefold()
        return tuple(item for item in self.references if item.domain.casefold() == normalized)

    def links_for(self, reference: DomainReference) -> tuple[CrossDomainLink, ...]:
        if not isinstance(reference, DomainReference):
            raise TypeError("reference must be a DomainReference")
        key = (reference.domain.casefold(), reference.reference_id)
        return tuple(
            link
            for link in self.links
            if (link.source.domain.casefold(), link.source.reference_id) == key
            or (link.target.domain.casefold(), link.target.reference_id) == key
        )

    def with_reference(self, reference: DomainReference) -> "CrossDomainContext":
        if not isinstance(reference, DomainReference):
            raise TypeError("reference must be a DomainReference")
        if (reference.domain.casefold(), reference.reference_id) in {
            (item.domain.casefold(), item.reference_id) for item in self.references
        }:
            raise CrossDomainContextValidationError("domain/reference pair already exists")
        return CrossDomainContext(
            context_state=self.context_state,
            goal_project=self.goal_project,
            situational=self.situational,
            references=self.references + (reference,),
            links=self.links,
        )

    def with_link(self, link: CrossDomainLink) -> "CrossDomainContext":
        if not isinstance(link, CrossDomainLink):
            raise TypeError("link must be a CrossDomainLink")
        if link in self.links:
            raise CrossDomainContextValidationError("link already exists")
        return CrossDomainContext(
            context_state=self.context_state,
            goal_project=self.goal_project,
            situational=self.situational,
            references=self.references,
            links=self.links + (link,),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_state": None if self.context_state is None else self.context_state.to_dict(),
            "goal_project": None if self.goal_project is None else self.goal_project.to_dict(),
            "situational": None if self.situational is None else self.situational.to_dict(),
            "references": [item.to_dict() for item in self.references],
            "links": [link.to_dict() for link in self.links],
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
