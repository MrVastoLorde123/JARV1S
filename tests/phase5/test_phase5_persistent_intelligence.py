from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.memory_episodic import EpisodicMemory, EpisodicOutcome
from src.core.memory_lifecycle import (
    MemoryTransition,
    propose_semantic_consolidation,
    validate_transition,
)
from src.core.memory_procedural import ProcedureStep, ProceduralMemory
from src.core.memory_provenance import (
    ProvenanceChain,
    ProvenanceRef,
    ProvenanceSourceKind,
    validate_provenance,
)
from src.core.memory_semantic import SemanticClaim, SemanticValidationStatus
from src.core.memory_working import WorkingMemorySnapshot
from src.core.personal_model import PersonalModelEntry, PersonalModelEntryKind
from src.core.persistent_intelligence import (
    PersistentIntelligenceSystem,
    PersistentMemoryRepository,
)
from src.core.persistent_memory import (
    MemoryLifecycle,
    PersistentMemoryKind,
    PersistentMemoryRecord,
)
from src.core.runtime_kernel import JarvisRuntime


class _StubOrchestration:
    def dispatch(self, *args, **kwargs):
        return {"status": "stub"}


class Phase5PersistentIntelligenceTests(unittest.TestCase):
    def _provenance(self) -> ProvenanceChain:
        return ProvenanceChain(
            refs=(
                ProvenanceRef(
                    provenance_id="prov-1",
                    source_kind=ProvenanceSourceKind.USER,
                    source_id="user-message-1",
                    summary="User supplied memory evidence",
                    observed_at="2026-09-17T00:00:00Z",
                    confidence=1.0,
                ),
            )
        )

    def _record(self, *, kind=PersistentMemoryKind.SEMANTIC, metadata=None, status=MemoryLifecycle.ACTIVE):
        return PersistentMemoryRecord(
            memory_id="memory-1",
            subject_id="user-1",
            kind=kind,
            content="JARVIS remembers a bounded claim.",
            confidence=0.8,
            importance=0.7,
            status=status,
            created_at="2026-09-17T00:00:00Z",
            updated_at="2026-09-17T00:00:00Z",
            provenance_ids=("prov-1",),
            metadata=metadata or {},
        )

    def test_canonical_record_enforces_bounded_confidence_and_non_authority_context(self):
        record = self._record()
        self.assertTrue(record.is_persistent)
        context = record.to_context()
        self.assertFalse(context["truth_established"])
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["execution_requested"])

        with self.assertRaises(ValueError):
            PersistentMemoryRecord(
                memory_id="m",
                subject_id="s",
                kind=PersistentMemoryKind.SEMANTIC,
                content="c",
                confidence=1.1,
            )

    def test_provenance_chain_is_deterministic_and_missing_refs_are_rejected(self):
        chain = self._provenance()
        same_chain = self._provenance()
        self.assertEqual(chain.digest, same_chain.digest)
        errors = validate_provenance(self._record(), chain)
        self.assertEqual(errors, ())

        missing = PersistentMemoryRecord(
            memory_id="memory-2",
            subject_id="user-1",
            kind=PersistentMemoryKind.SEMANTIC,
            content="missing evidence",
            confidence=0.5,
            provenance_ids=("missing",),
            created_at="2026-09-17T00:00:00Z",
            updated_at="2026-09-17T00:00:00Z",
        )
        self.assertTrue(validate_provenance(missing, chain))

    def test_episodic_memory_preserves_event_and_outcome(self):
        episode = EpisodicMemory(
            memory_id="episode-1",
            subject_id="user-1",
            event_type="WORK_SESSION",
            summary="Completed a systems-engineering task.",
            observed_at="2026-09-17T00:00:00Z",
            outcome=EpisodicOutcome.SUCCEEDED,
            provenance_ids=("prov-1",),
        )
        record = episode.to_record()
        self.assertEqual(record.kind, PersistentMemoryKind.EPISODIC)
        self.assertEqual(record.metadata["outcome"], "SUCCEEDED")
        self.assertEqual(record.metadata["event_type"], "WORK_SESSION")

    def test_semantic_claim_requires_provenance_and_does_not_establish_truth(self):
        claim = SemanticClaim(
            memory_id="semantic-1",
            subject_id="user-1",
            subject="user-1",
            predicate="prefers",
            object_value="hands-on systems work",
            provenance_ids=("prov-1",),
            validation=SemanticValidationStatus.SUPPORTED,
        )
        self.assertEqual(claim.validate_against(self._provenance()), ())
        record = claim.to_record(observed_at="2026-09-17T00:00:00Z")
        self.assertEqual(record.kind, PersistentMemoryKind.SEMANTIC)
        self.assertEqual(record.metadata["validation"], "SUPPORTED")
        self.assertFalse(record.to_context()["truth_established"])

    def test_procedural_memory_describes_steps_without_execution_authority(self):
        procedure = ProceduralMemory(
            memory_id="procedure-1",
            subject_id="user-1",
            name="Network diagnostics",
            purpose="Diagnose a reachable network endpoint.",
            steps=(
                ProcedureStep("step-1", "Check reachability", verification="Require an observed response."),
                ProcedureStep("step-2", "Inspect path", prerequisites=("step-1",), capability_id="network-read"),
            ),
            provenance_ids=("prov-1",),
        )
        record = procedure.to_record(observed_at="2026-09-17T00:00:00Z")
        self.assertEqual(record.kind, PersistentMemoryKind.PROCEDURAL)
        self.assertFalse(record.metadata["execution_authorized"])
        self.assertFalse(hasattr(procedure, "execute"))

    def test_working_memory_is_contextual_and_not_durably_persisted(self):
        snapshot = WorkingMemorySnapshot(
            session_id="session-1",
            version=1,
            focus="Phase 5",
            memory_ids=("memory-1",),
            assumptions=("memory is evidence",),
            open_questions=("what should be consolidated?",),
            created_at="2026-09-17T00:00:00Z",
        )
        context = snapshot.to_context()
        self.assertFalse(context["durable_mutation_performed"])

        with tempfile.TemporaryDirectory() as directory:
            repository = PersistentMemoryRepository(Path(directory) / "jarvis.db")
            working = self._record(kind=PersistentMemoryKind.WORKING)
            with self.assertRaises(ValueError):
                repository.persist(working, self._provenance())

    def test_personal_model_active_entries_require_memory_support(self):
        entry = PersonalModelEntry(
            entry_id="entry-1",
            kind=PersonalModelEntryKind.PREFERENCE,
            statement="Prefers deterministic verification before integration.",
            confidence=0.9,
            provenance_ids=("prov-1",),
            source_memory_id="memory-1",
        )
        self.assertFalse(entry.to_context()["user_intent_established"])

        system = PersistentIntelligenceSystem(
            PersistentMemoryRepository(Path(tempfile.mkdtemp()) / "jarvis.db")
        )
        model = system.project_personal_model("user-1", (entry,), model_version=2)
        self.assertEqual(model.model_version, 2)
        self.assertEqual(len(model.active_entries()), 1)

        invalid = PersonalModelEntry(
            entry_id="entry-2",
            kind=PersonalModelEntryKind.GOAL,
            statement="Ship reliable software.",
            confidence=0.8,
            provenance_ids=("prov-1",),
        )
        with self.assertRaises(ValueError):
            system.project_personal_model("user-1", (invalid,))

    def test_memory_lifecycle_accepts_active_to_superseded_and_rejects_archived_reactivation(self):
        active = self._record()
        transition = MemoryTransition(
            memory_id="memory-1",
            from_status=MemoryLifecycle.ACTIVE,
            to_status=MemoryLifecycle.SUPERSEDED,
            reason="A later supported claim superseded this memory.",
            evidence_ids=("prov-1",),
        )
        self.assertEqual(validate_transition(active, transition), ())

        archived = self._record(status=MemoryLifecycle.ARCHIVED)
        invalid = MemoryTransition(
            memory_id="memory-1",
            from_status=MemoryLifecycle.ARCHIVED,
            to_status=MemoryLifecycle.ACTIVE,
            reason="Invalid reactivation",
        )
        self.assertTrue(validate_transition(archived, invalid))

    def test_consolidation_only_proposes_repeated_semantic_patterns(self):
        episode_one = EpisodicMemory(
            memory_id="episode-1",
            subject_id="user-1",
            event_type="STUDY",
            summary="Practiced networking fundamentals.",
            observed_at="2026-09-17T00:00:00Z",
            provenance_ids=("prov-1",),
        )
        episode_two = EpisodicMemory(
            memory_id="episode-2",
            subject_id="user-1",
            event_type="STUDY",
            summary="Practiced networking fundamentals.",
            observed_at="2026-09-17T01:00:00Z",
            provenance_ids=("prov-1",),
        )
        proposals = propose_semantic_consolidation((episode_one, episode_two))
        self.assertEqual(len(proposals), 1)
        self.assertEqual(proposals[0].source_memory_ids, ("episode-1", "episode-2"))
        self.assertEqual(proposals[0].proposed_kind, "SEMANTIC")

    def test_repository_persists_and_recalls_provenance_backed_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = PersistentMemoryRepository(Path(directory) / "jarvis.db")
            system = PersistentIntelligenceSystem(repository)
            record = self._record(metadata={"nested": ("a", "b")})
            self.assertTrue(system.remember(record, self._provenance()))
            restored = system.recall()[0]
            self.assertEqual(restored.memory_id, "memory-1")
            self.assertEqual(restored.kind, PersistentMemoryKind.SEMANTIC)
            self.assertEqual(restored.metadata["nested"], ["a", "b"])
            restored_provenance = system.provenance("memory-1")
            self.assertEqual(restored_provenance.ids, ("prov-1",))

    def test_repository_remember_is_idempotent_for_identical_records(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = PersistentMemoryRepository(Path(directory) / "jarvis.db")
            system = PersistentIntelligenceSystem(repository)
            record = self._record(metadata={"steps": ("one", "two")})
            self.assertTrue(system.remember(record, self._provenance()))
            self.assertFalse(system.remember(record, self._provenance()))
            self.assertEqual(len(system.recall()), 1)

    def test_repository_applies_only_valid_lifecycle_transitions(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = PersistentMemoryRepository(Path(directory) / "jarvis.db")
            system = PersistentIntelligenceSystem(repository)
            record = self._record()
            system.remember(record, self._provenance())
            transition = MemoryTransition(
                memory_id="memory-1",
                from_status=MemoryLifecycle.ACTIVE,
                to_status=MemoryLifecycle.SUPERSEDED,
                reason="superseded by a newer memory",
                evidence_ids=("prov-1",),
            )
            updated = system.transition(transition, updated_at="2026-09-17T02:00:00Z")
            self.assertEqual(updated.status, MemoryLifecycle.SUPERSEDED)

    def test_persistent_intelligence_summary_reports_no_authority_or_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            system = PersistentIntelligenceSystem(
                PersistentMemoryRepository(Path(directory) / "jarvis.db")
            )
            summary = system.summary()
            self.assertFalse(summary["authority_granted"])
            self.assertFalse(summary["execution_requested"])
            self.assertFalse(summary["capability_invocation_performed"])
            self.assertFalse(summary["provider_selected"])
            self.assertFalse(system.to_context()["authority_granted"])

    def test_runtime_accepts_persistent_intelligence_without_gaining_execution_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            persistent = PersistentIntelligenceSystem(
                PersistentMemoryRepository(Path(directory) / "jarvis.db")
            )
            runtime = JarvisRuntime(
                orchestration=_StubOrchestration(),
                session_id="session-1",
                actor_id="user-1",
                persistent_intelligence=persistent,
            )
            self.assertIs(runtime.persistent_intelligence, persistent)
            self.assertFalse(runtime.authorizes_execution)
            self.assertFalse(runtime.executes_capability)
            self.assertFalse(runtime.mutates_state)
            self.assertFalse(runtime.persists_state)

    def test_persistent_intelligence_core_has_no_authority_execution_or_provider_surface(self):
        source = Path("src/core/persistent_intelligence.py").read_text(encoding="utf-8")
        forbidden = (
            "def execute(",
            "authorize(",
            "run_execution_handoff(",
            "select_provider",
            "provider_call(",
            "subprocess",
        )
        for marker in forbidden:
            self.assertNotIn(marker, source, marker)


if __name__ == "__main__":
    unittest.main()
