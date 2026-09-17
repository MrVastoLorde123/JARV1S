"""Structural verification for the Phase 10 cognitive runtime boundary."""
from __future__ import annotations

from src.core.cognitive_runtime import CognitiveRuntime
from src.core.planning_decision import PlanningDecisionSystem
from src.core.proactive_initiative import ProactiveInitiativeSystem
from src.core.reasoning import ReasoningSystem
from src.core.world_model import WorldModelSystem
from src.core.runtime_kernel import JarvisRuntime


class _Orchestration:
    def dispatch(self, request):
        from src.core.interface_backend import InterfaceResponse, InterfaceResponseStatus

        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={},
        )


def main() -> None:
    cognitive = CognitiveRuntime(
        world_model=WorldModelSystem(),
        reasoning_system=ReasoningSystem(),
        planning_system=PlanningDecisionSystem(),
        proactive_initiative=ProactiveInitiativeSystem(),
    )
    assert cognitive.authorizes_execution is False
    assert cognitive.executes_capability is False
    assert cognitive.mutates_external_state is False
    assert cognitive.persists_state is False
    assert cognitive.establishes_truth is False
    assert cognitive.establishes_certainty is False
    assert cognitive.selects_provider is False

    runtime = JarvisRuntime(
        orchestration=_Orchestration(),
        session_id="phase10-structural-session",
        actor_id="phase10-structural-actor",
    )
    assert isinstance(runtime.cognitive_runtime, CognitiveRuntime)
    assert runtime.world_model is runtime.cognitive_runtime.world_model
    assert runtime.reasoning_system is runtime.cognitive_runtime.reasoning_system
    assert runtime.planning_system is runtime.cognitive_runtime.planning_system
    assert runtime.proactive_initiative is runtime.cognitive_runtime.proactive_initiative
    assert runtime.authorizes_execution is False
    assert runtime.executes_capability is False
    assert runtime.mutates_state is False
    assert runtime.persists_state is False
    assert runtime.establishes_truth is False
    assert runtime.establishes_certainty is False
    assert runtime.is_ai_provider is False

    print("PHASE 10 STRUCTURAL VERIFIER: PASS")


if __name__ == "__main__":
    main()
