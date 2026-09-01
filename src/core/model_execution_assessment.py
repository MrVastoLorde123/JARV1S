import json

from src.ai.models import AIRequest
from src.ai.service import AIService
from src.core.execution_assessment import ExecutionAssessment, ExecutionAssessmentService
from src.core.execution_state import ExecutionState


class ModelExecutionAssessmentService:
    """
    Model-assisted interpretation of verified execution state.

    The model may interpret the situation and remaining work, but verified
    execution outputs remain sourced from the deterministic assessment.
    This service never validates, authorizes, confirms, or executes actions.
    """

    def __init__(
        self,
        ai_service: AIService,
        deterministic_service: ExecutionAssessmentService | None = None,
        provider_name: str | None = None,
    ):
        if not isinstance(ai_service, AIService):
            raise TypeError("ai_service must be an AIService.")
        if deterministic_service is not None and not isinstance(
            deterministic_service, ExecutionAssessmentService
        ):
            raise TypeError(
                "deterministic_service must be an ExecutionAssessmentService or None."
            )
        self.ai_service = ai_service
        self.deterministic_service = deterministic_service or ExecutionAssessmentService()
        self.provider_name = provider_name

    def assess(self, state: ExecutionState) -> ExecutionAssessment:
        if not isinstance(state, ExecutionState):
            raise TypeError("state must be an ExecutionState.")

        baseline = self.deterministic_service.assess(state)
        prompt = (
            "Interpret the verified execution state for the objective. "
            "Return ONLY JSON with keys 'situation', 'completed', 'remaining', "
            "'blockers', 'recommended_next_action', and 'confidence'. "
            "Do not invent execution results. Do not claim that anything was "
            "executed beyond the verified state. Keep completed work grounded "
            "in the observed state, and identify the smallest remaining work "
            "needed for the objective. Confidence must be a number from 0.0 to 1.0.\n\n"
            f"Verified execution state: {json.dumps(state.to_context(), default=str)}\n"
            f"Deterministic baseline assessment: {json.dumps(baseline.to_context(), default=str)}\n"
        )

        response = self.ai_service.generate(
            AIRequest(
                task=prompt,
                context={
                    "type": "execution_assessment",
                    "goal": state.goal,
                    "execution_state": state.to_context(),
                    "deterministic_assessment": baseline.to_context(),
                },
                metadata={"purpose": "execution_state_reasoning"},
            ),
            provider_name=self.provider_name,
        )

        parsed = self._parse(response.content)
        return ExecutionAssessment(
            goal=state.goal,
            situation=parsed["situation"],
            completed=parsed["completed"],
            remaining=parsed["remaining"],
            blockers=parsed["blockers"],
            useful_outputs=baseline.useful_outputs,
            recommended_next_action=parsed["recommended_next_action"],
            confidence=parsed["confidence"],
        )

    @staticmethod
    def _parse(content) -> dict:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Assessment model returned empty output.")

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Assessment model returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Assessment model output must be a JSON object.")

        required = (
            "situation",
            "completed",
            "remaining",
            "blockers",
            "recommended_next_action",
            "confidence",
        )
        missing = [key for key in required if key not in payload]
        if missing:
            raise ValueError(
                "Assessment model output is missing required keys: " + ", ".join(missing)
            )

        situation = payload["situation"]
        if not isinstance(situation, str) or not situation.strip():
            raise ValueError("Assessment situation must be a non-empty string.")

        collections = {}
        for key in ("completed", "remaining", "blockers"):
            value = payload[key]
            if not isinstance(value, list) or any(
                not isinstance(item, str) or not item.strip() for item in value
            ):
                raise ValueError(f"Assessment {key} must be a list of non-empty strings.")
            collections[key] = tuple(item.strip() for item in value)

        recommendation = payload["recommended_next_action"]
        if recommendation is not None:
            if not isinstance(recommendation, str) or not recommendation.strip():
                raise ValueError(
                    "Assessment recommended_next_action must be a string or null."
                )
            recommendation = recommendation.strip()

        confidence = payload["confidence"]
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
            raise ValueError("Assessment confidence must be a number from 0.0 to 1.0.")
        confidence = float(confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Assessment confidence must be a number from 0.0 to 1.0.")

        return {
            "situation": situation.strip(),
            **collections,
            "recommended_next_action": recommendation,
            "confidence": confidence,
        }
