"""Focused Phase 3 systems-intelligence verification suite."""

from __future__ import annotations

import unittest

from src.core.capability_compounding import (
    CapabilityCompoundingEvidence,
    CapabilityCompoundingLink,
)
from src.core.capability_composition import (
    CapabilityComposition,
    CapabilityCompositionStep,
)
from src.core.capability_graph import (
    CapabilityGraph,
    CapabilityRelation,
    CapabilityRelationKind,
    build_capability_graph,
)
from src.core.capability_registry import CapabilityDefinition, CapabilityRegistry
from src.core.capability_system import CapabilitySystem
from src.core.capability_utility import CapabilityUtilityProfile, CapabilityUtilityWeights
from src.core.runtime_kernel import JarvisRuntime


class _Orchestration:
    def dispatch(self, request):
        from src.core.interface_backend import InterfaceResponse, InterfaceResponseStatus

        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={"artifact_type": "TEST_STAGE"},
        )


class Phase3SystemsIntelligenceTests(unittest.TestCase):
    def definition(self, capability_id: str, name: str | None = None) -> CapabilityDefinition:
        return CapabilityDefinition(
            capability_id=capability_id,
            name=name or capability_id,
            description=f"Capability {capability_id}",
            category="systems-intelligence",
            metadata={},
        )

    def graph(self) -> CapabilityGraph:
        capabilities = (
            self.definition("collect"),
            self.definition("analyze"),
            self.definition("publish"),
        )
        return build_capability_graph(
            capabilities,
            (
                CapabilityRelation(
                    "analyze",
                    "collect",
                    CapabilityRelationKind.DEPENDS_ON,
                    "analysis requires collected data",
                ),
                CapabilityRelation(
                    "publish",
                    "analyze",
                    CapabilityRelationKind.DEPENDS_ON,
                    "publishing requires analysis",
                ),
                CapabilityRelation(
                    "collect",
                    "analyze",
                    CapabilityRelationKind.ENABLES,
                    "fresh data improves analysis availability",
                ),
            ),
        )

    def test_graph_preserves_declared_relationships_without_execution_surface(self) -> None:
        graph = self.graph()
        self.assertEqual(graph.capability_ids, ("collect", "analyze", "publish"))
        self.assertEqual(
            graph.relations_from("analyze", kind=CapabilityRelationKind.DEPENDS_ON)[0].target_capability_id,
            "collect",
        )
        self.assertFalse(hasattr(graph, "authorize"))
        self.assertFalse(hasattr(graph, "execute"))

    def test_dependency_model_resolves_transitive_closure_and_readiness(self) -> None:
        system = CapabilitySystem(self.graph())
        self.assertEqual(system.dependency_model.direct_dependencies("publish"), ("analyze",))
        self.assertEqual(
            system.dependency_model.transitive_dependencies("publish"),
            ("collect", "analyze"),
        )
        self.assertEqual(system.dependency_model.dependency_depth("publish"), 2)
        assessment = system.dependency_model.assess(
            "publish",
            available_capabilities=("collect",),
        )
        self.assertFalse(assessment.ready)
        self.assertEqual(assessment.missing_dependencies, ("analyze",))

    def test_dependency_cycle_is_rejected(self) -> None:
        graph = build_capability_graph(
            (self.definition("a"), self.definition("b")),
            (
                CapabilityRelation("a", "b", CapabilityRelationKind.DEPENDS_ON, "a needs b"),
                CapabilityRelation("b", "a", CapabilityRelationKind.DEPENDS_ON, "b needs a"),
            ),
        )
        with self.assertRaises(ValueError):
            CapabilitySystem(graph)

    def test_utility_model_calculates_normalized_score(self) -> None:
        weights = CapabilityUtilityWeights(
            frequency=0.0,
            impact=0.5,
            reliability=0.5,
            scalability=0.0,
            cost=0.0,
            failure_rate=0.0,
        )
        profile = CapabilityUtilityProfile(
            capability_id="analyze",
            frequency=0.1,
            impact=0.8,
            reliability=0.6,
            scalability=0.9,
            cost=0.2,
            failure_rate=0.1,
            evidence_count=4,
        )
        system = CapabilitySystem(self.graph(), utility_profiles=(profile,), utility_weights=weights)
        self.assertAlmostEqual(system.utility_model.utility_score("analyze"), 0.7)
        self.assertEqual(system.utility_model.profile("analyze").evidence_count, 4)

    def test_composition_requires_all_component_dependencies(self) -> None:
        system = CapabilitySystem(
            self.graph(),
            compositions=(
                CapabilityComposition(
                    composition_id="reporting-loop",
                    output_capability_id="report",
                    steps=(
                        CapabilityCompositionStep(0, "collect", "gather inputs"),
                        CapabilityCompositionStep(1, "analyze", "interpret inputs"),
                        CapabilityCompositionStep(2, "publish", "publish result"),
                    ),
                    rationale="combine the three declared capabilities into a higher-order result",
                ),
            ),
        )
        not_ready = system.assess_composition_readiness(
            "reporting-loop",
            available_capabilities=("collect", "analyze"),
        )
        self.assertFalse(not_ready.ready)
        self.assertEqual(not_ready.missing_capabilities, ("publish",))
        ready = system.assess_composition_readiness(
            "reporting-loop",
            available_capabilities=("collect", "analyze", "publish"),
        )
        self.assertTrue(ready.ready)

    def test_compounding_gain_is_discounted_by_confidence(self) -> None:
        system = CapabilitySystem(
            self.graph(),
            utility_profiles=(
                CapabilityUtilityProfile(
                    capability_id="collect",
                    frequency=1.0,
                    impact=1.0,
                    reliability=1.0,
                    scalability=1.0,
                    cost=0.0,
                    failure_rate=0.0,
                ),
            ),
            compounding_links=(
                CapabilityCompoundingLink(
                    source_capability_id="collect",
                    target_capability_id="analyze",
                    mechanism="fresh collection increases analysis usefulness",
                    utility_gain=0.8,
                    confidence=0.5,
                    evidence=CapabilityCompoundingEvidence.OBSERVED,
                ),
            ),
        )
        assessment = system.compounding_model.assess("collect")
        self.assertAlmostEqual(assessment.total_weighted_gain, 0.4)
        self.assertAlmostEqual(assessment.leveraged_utility, 1.0)
        self.assertEqual(assessment.outgoing_links[0].evidence, CapabilityCompoundingEvidence.OBSERVED)

    def test_system_assessment_exposes_compounding_and_composition_without_ranking_authority(self) -> None:
        composition = CapabilityComposition(
            composition_id="analyze-and-publish",
            output_capability_id="report",
            steps=(
                CapabilityCompositionStep(0, "analyze", "interpret"),
                CapabilityCompositionStep(1, "publish", "publish"),
            ),
            rationale="turn analysis into a report",
        )
        system = CapabilitySystem(
            self.graph(),
            compositions=(composition,),
            compounding_links=(
                CapabilityCompoundingLink(
                    "analyze",
                    "publish",
                    "analysis increases usefulness of publication",
                    0.6,
                    0.5,
                ),
            ),
        )
        assessment = system.assess("analyze")
        self.assertEqual(assessment.dependency_count, 1)
        self.assertEqual(assessment.composition_count, 1)
        self.assertEqual(assessment.outgoing_compounding_link_count, 1)
        self.assertAlmostEqual(assessment.total_weighted_compounding_gain, 0.3)
        self.assertFalse(system.summary()["authority_granted"])

    def test_system_can_snapshot_from_registry(self) -> None:
        registry = CapabilityRegistry()
        definitions = (
            self.definition("collect"),
            self.definition("analyze"),
            self.definition("publish"),
        )
        for definition in definitions:
            registry.register(definition)
        system = CapabilitySystem.from_registry(registry)
        self.assertEqual(system.capability_ids, ("collect", "analyze", "publish"))

    def test_runtime_can_expose_injected_capability_system(self) -> None:
        system = CapabilitySystem(self.graph())
        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="phase3-session",
            actor_id="phase3-actor",
            capability_system=system,
        )
        self.assertIs(runtime.capability_system, system)
        self.assertFalse(runtime.authorizes_execution)
        self.assertFalse(runtime.executes_capability)

    def test_runtime_rejects_an_invalid_capability_system_type(self) -> None:
        with self.assertRaises(TypeError):
            JarvisRuntime(
                orchestration=_Orchestration(),
                session_id="phase3-session",
                actor_id="phase3-actor",
                capability_system=object(),
            )

    def test_system_does_not_offer_execution_or_authority_methods(self) -> None:
        system = CapabilitySystem(self.graph())
        for method in ("authorize", "execute", "invoke", "select_provider", "select_tool"):
            self.assertFalse(hasattr(system, method), method)


if __name__ == "__main__":
    unittest.main()
