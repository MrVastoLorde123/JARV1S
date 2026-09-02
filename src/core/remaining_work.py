from dataclasses import dataclass
from typing import Any

from src.core.execution_assessment import ExecutionAssessment
from src.core.execution_state import ExecutionState


@dataclass(frozen=True)
class RemainingWork:
    """Deterministic, state-grounded representation of work still required."""

    goal: str
    items: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    source_requirements: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise ValueError("goal must be a non-empty string.")
        for collection, name in (
            (self.items, "items"),
            (self.blockers, "blockers"),
            (self.source_requirements, "source_requirements"),
        ):
            if not isinstance(collection, tuple):
                raise TypeError(f"{name} must be a tuple.")
            for value in collection:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{name} entries must be non-empty strings.")

    def to_context(self) -> dict[str, Any]:
        """Return a provider-neutral representation for downstream planning."""
        return {
            "goal": self.goal,
            "items": self.items,
            "blockers": self.blockers,
            "source_requirements": self.source_requirements,
        }


class RemainingWorkResolver:
    """Resolve model-described remaining work against verified execution state."""

    def resolve(
        self,
        state: ExecutionState,
        assessment: ExecutionAssessment,
    ) -> RemainingWork:
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState.")
        if not isinstance(assessment, ExecutionAssessment):
            raise TypeError("assessment must be an ExecutionAssessment.")
        if assessment.goal != state.goal:
            raise ValueError("Assessment goal does not match execution state goal.")

        if state.status.value == "COMPLETED":
            return RemainingWork(goal=state.goal)

        required = tuple(state.unresolved_requirements)
        items: list[str] = []

        # Observed unresolved requirements are mandatory remaining work.
        items.extend(required)

        # Preserve model-supplied remaining work only when it does not
        # contradict or disappear behind the observed failure boundary.
        for candidate in assessment.remaining:
            if self._matches_any(candidate, required):
                if candidate not in items:
                    items.append(candidate)
                continue

            if not required and self._matches_failed_step(candidate, state):
                if candidate not in items:
                    items.append(candidate)

        blockers = list(required)
        for blocker in assessment.blockers:
            if self._matches_any(blocker, blockers):
                if blocker not in blockers:
                    blockers.append(blocker)

        return RemainingWork(
            goal=state.goal,
            items=tuple(items),
            blockers=tuple(blockers),
            source_requirements=required,
        )

    @classmethod
    def _matches_failed_step(cls, candidate: str, state: ExecutionState) -> bool:
        candidate_tokens = cls._tokens(candidate)
        if not candidate_tokens:
            return False
        return any(
            cls._claims_same_step(candidate, step_id)
            for step_id in state.failed_steps
        )

    @classmethod
    def _matches_any(cls, candidate: str, values: tuple[str, ...] | list[str]) -> bool:
        return any(cls._claims_same_requirement(candidate, value) for value in values)

    @classmethod
    def _claims_same_step(cls, claim: str, step: str) -> bool:
        claim_tokens = cls._tokens(claim)
        step_tokens = cls._tokens(step)
        if not claim_tokens or not step_tokens:
            return False
        return (
            claim_tokens == step_tokens
            or step_tokens.issubset(claim_tokens)
            or claim_tokens.issubset(step_tokens)
            or "".join(step_tokens) in "".join(claim_tokens)
            or "".join(claim_tokens) in "".join(step_tokens)
        )

    @classmethod
    def _claims_same_requirement(cls, claim: str, requirement: str) -> bool:
        claim_tokens = cls._tokens(claim)
        requirement_tokens = cls._tokens(requirement)
        if not claim_tokens or not requirement_tokens:
            return False

        overlap = claim_tokens & requirement_tokens
        meaningful_requirement = requirement_tokens - {
            "resolve",
            "failed",
            "step",
            "error",
            "required",
            "requirement",
        }
        return bool(overlap & meaningful_requirement)

    @staticmethod
    def _tokens(value: str) -> set[str]:
        import re

        return set(re.findall(r"[a-z0-9]+", value.lower()))
