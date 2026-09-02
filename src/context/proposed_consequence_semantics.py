"""Semantic contract for proposed consequences after reasoning and prioritization.

M7.4 represents action-shaped recommendations without granting permission to
execute them. A proposal may describe a desired consequence, why it was
proposed, and what attention target motivated it, but it contains no tool
handle, authorization decision, or executable payload.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.context.interpretation_semantics import Interpretation
from src.context.prioritization_semantics import Prioritization
from src.context.reasoning_semantics import ReasoningContext


class ConsequenceKind(str, Enum):
    ANSWER = "answer"
    ASK = "ask"
    INVESTIGATE = "investigate"
    PREPARE = "prepare"
    DEFER = "defer"
    PLAN = "plan"


@dataclass(frozen=True)
class ProposalSupport:
    """References to reasoning artifacts that justify a proposal."""

    source_kind: str
    source_id: str

    def __post_init__(self):
        if not isinstance(self.source_kind, str) or not self.source_kind.strip():
            raise ValueError("source_kind must be a non-empty string.")
        if not isinstance(self.source_id, str) or not self.source_id.strip():
            raise ValueError("source_id must be a non-empty string.")


@dataclass(frozen=True)
class ProposedConsequence:
    """Action-shaped recommendation with no authorization or execution power."""

    consequence: str
    kind: ConsequenceKind
    support: tuple[ProposalSupport, ...] = ()
    priority_target_id: str | None = None
    confidence: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.consequence, str) or not self.consequence.strip():
            raise ValueError("consequence must be a non-empty string.")
        if not isinstance(self.kind, ConsequenceKind):
            raise TypeError("kind must be a ConsequenceKind value.")
        if not isinstance(self.support, tuple):
            raise TypeError("support must be a tuple.")
        if any(not isinstance(item, ProposalSupport) for item in self.support):
            raise TypeError("support must contain ProposalSupport values.")
        if self.priority_target_id is not None and (
            not isinstance(self.priority_target_id, str) or not self.priority_target_id.strip()
        ):
            raise ValueError("priority_target_id must be a non-empty string when provided.")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")
        forbidden = {"authorize", "authorization", "execute", "execution", "tool_handle"}
        if any(key in forbidden for key in self.metadata):
            raise ValueError("proposals cannot carry authorization or execution controls.")


@dataclass(frozen=True)
class ProposedConsequences:
    """Complete non-authoritative consequence proposals for one request."""

    request: str
    proposals: tuple[ProposedConsequence, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.proposals, tuple):
            raise TypeError("proposals must be a tuple.")
        if any(not isinstance(item, ProposedConsequence) for item in self.proposals):
            raise TypeError("proposals must contain ProposedConsequence values.")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping.")

    def to_context(self) -> dict[str, Any]:
        return {
            "request": self.request,
            "proposals": tuple(
                {
                    "consequence": proposal.consequence,
                    "kind": proposal.kind.value,
                    "support": tuple(
                        {"source_kind": ref.source_kind, "source_id": ref.source_id}
                        for ref in proposal.support
                    ),
                    "priority_target_id": proposal.priority_target_id,
                    "confidence": proposal.confidence,
                    "metadata": dict(proposal.metadata),
                    "epistemic_role": "proposed",
                    "authorization": False,
                }
                for proposal in self.proposals
            ),
            "metadata": dict(self.metadata),
        }


class ProposedConsequenceProjector:
    """Create proposals from reasoning and attention without authorizing actions."""

    def project(
        self,
        reasoning_context: ReasoningContext,
        prioritization: Prioritization,
        interpretation: Interpretation | None = None,
    ) -> ProposedConsequences:
        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if not isinstance(prioritization, Prioritization):
            raise TypeError("prioritization must be a Prioritization.")
        if prioritization.request != reasoning_context.request:
            raise ValueError("prioritization request must match reasoning context request.")
        if interpretation is not None and not isinstance(interpretation, Interpretation):
            raise TypeError("interpretation must be an Interpretation or None.")
        if interpretation is not None and interpretation.request != reasoning_context.request:
            raise ValueError("interpretation request must match reasoning context request.")

        proposals = []
        if prioritization.targets:
            top = prioritization.targets[0]
            proposals.append(
                ProposedConsequence(
                    consequence=f"Address the highest-priority concern: {top.description}",
                    kind=ConsequenceKind.PLAN,
                    support=(ProposalSupport("prioritization", top.target_id),),
                    priority_target_id=top.target_id,
                )
            )

        if interpretation is not None:
            if interpretation.conflicts:
                proposals.append(
                    ProposedConsequence(
                        consequence="Resolve the identified conflict before treating the conclusion as settled.",
                        kind=ConsequenceKind.INVESTIGATE,
                        support=tuple(
                            ProposalSupport("conflict", str(index))
                            for index, _ in enumerate(interpretation.conflicts)
                        ),
                    )
                )
            elif interpretation.missing_information:
                proposals.append(
                    ProposedConsequence(
                        consequence="Obtain the missing information needed to proceed confidently.",
                        kind=ConsequenceKind.ASK,
                        support=tuple(
                            ProposalSupport("missing_information", str(index))
                            for index, _ in enumerate(interpretation.missing_information)
                        ),
                    )

        return ProposedConsequences(
            request=reasoning_context.request,
            proposals=tuple(proposals),
            metadata={"proposal_semantics": "m7.4"},
        )


class ProposedConsequenceValidator:
    """Validate proposal boundaries without granting execution authority."""

    _FORBIDDEN_KEYS = {"authorize", "authorization", "execute", "execution", "tool_handle"}

    def validate(
        self,
        reasoning_context: ReasoningContext,
        prioritization: Prioritization,
        proposals: ProposedConsequences,
        interpretation: Interpretation | None = None,
    ) -> None:
        if not isinstance(reasoning_context, ReasoningContext):
            raise TypeError("reasoning_context must be a ReasoningContext.")
        if not isinstance(prioritization, Prioritization):
            raise TypeError("prioritization must be a Prioritization.")
        if not isinstance(proposals, ProposedConsequences):
            raise TypeError("proposals must be a ProposedConsequences.")
        if prioritization.request != reasoning_context.request:
            raise ValueError("prioritization request must match reasoning context request.")
        if proposals.request != reasoning_context.request:
            raise ValueError("proposals request must match reasoning context request.")
        if interpretation is not None:
            if not isinstance(interpretation, Interpretation):
                raise TypeError("interpretation must be an Interpretation or None.")
            if interpretation.request != reasoning_context.request:
                raise ValueError("interpretation request must match reasoning context request.")

        target_ids = {target.target_id for target in prioritization.targets}
        for proposal in proposals.proposals:
            if proposal.priority_target_id is not None and proposal.priority_target_id not in target_ids:
                raise ValueError("proposal priority target must reference the supplied prioritization.")
            if any(ref.source_kind == "prioritization" and ref.source_id not in target_ids for ref in proposal.support):
                raise ValueError("proposal prioritization support must reference a known priority target.")
            if any(key in self._FORBIDDEN_KEYS for key in proposal.metadata):
                raise ValueError("proposals cannot contain authorization or execution controls.")
