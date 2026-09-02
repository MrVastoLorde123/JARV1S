import re

from src.core.execution_assessment import ExecutionAssessment
from src.core.execution_state import ExecutionState


class ExecutionAssessmentValidator:
    """Validate model interpretation against observed execution reality."""

    def validate(
        self,
        state: ExecutionState,
        assessment: ExecutionAssessment,
    ) -> ExecutionAssessment:
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState.")
        if not isinstance(assessment, ExecutionAssessment):
            raise TypeError("assessment must be an ExecutionAssessment.")
        if assessment.goal != state.goal:
            raise ValueError("Assessment goal does not match observed execution state.")

        self._validate_situation(state, assessment)
        self._validate_completed_claims(state, assessment)
        self._validate_observed_blockers(state, assessment)

        return assessment

    @staticmethod
    def _validate_situation(
        state: ExecutionState,
        assessment: ExecutionAssessment,
    ) -> None:
        if state.status.value == "COMPLETED" and assessment.situation != "objective_completed":
            raise ValueError(
                "Assessment situation conflicts with observed completed execution."
            )

        if state.status.value != "COMPLETED" and assessment.situation == "objective_completed":
            raise ValueError(
                "Assessment claims objective completion despite non-completed execution."
            )

    @classmethod
    def _validate_completed_claims(
        cls,
        state: ExecutionState,
        assessment: ExecutionAssessment,
    ) -> None:
        observed_completed = tuple(state.completed_steps)
        observed_failed = tuple(state.failed_steps)

        for claim in assessment.completed:
            failed_match = cls._find_matching_step(claim, observed_failed)
            if failed_match is not None:
                raise ValueError(
                    f"Assessment claims failed step '{failed_match}' as completed."
                )

            completed_match = cls._find_matching_step(claim, observed_completed)
            if completed_match is None:
                raise ValueError(
                    f"Assessment completed claim '{claim}' is not grounded in an observed completed step."
                )

    @classmethod
    def _validate_observed_blockers(
        cls,
        state: ExecutionState,
        assessment: ExecutionAssessment,
    ) -> None:
        if not state.unresolved_requirements:
            return

        for requirement in state.unresolved_requirements:
            if not any(
                cls._claims_same_requirement(requirement, blocker)
                for blocker in assessment.blockers
            ):
                raise ValueError(
                    "Assessment blockers omit an observed unresolved requirement: "
                    f"'{requirement}'."
                )

    @classmethod
    def _find_matching_step(
        cls,
        claim: str,
        steps: tuple[str, ...],
    ) -> str | None:
        for step in steps:
            if cls._claims_same_step(claim, step):
                return step
        return None

    @classmethod
    def _claims_same_step(cls, claim: str, step: str) -> bool:
        claim_tokens = cls._tokens(claim)
        step_tokens = cls._tokens(step)
        if not claim_tokens or not step_tokens:
            return False

        if claim_tokens == step_tokens:
            return True
        if step_tokens.issubset(claim_tokens):
            return True
        if claim_tokens.issubset(step_tokens):
            return True

        claim_compact = "".join(claim_tokens)
        step_compact = "".join(step_tokens)
        return step_compact in claim_compact or claim_compact in step_compact

    @classmethod
    def _claims_same_requirement(cls, requirement: str, blocker: str) -> bool:
        requirement_tokens = cls._tokens(requirement)
        blocker_tokens = cls._tokens(blocker)
        if not requirement_tokens or not blocker_tokens:
            return False

        # A model may summarize an observed requirement, so require meaningful
        # lexical overlap while allowing it to omit boilerplate such as the
        # failed-step prefix.
        overlap = requirement_tokens & blocker_tokens
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
        return set(re.findall(r"[a-z0-9]+", value.lower()))
