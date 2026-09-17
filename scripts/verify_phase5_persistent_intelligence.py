"""Static contract verifier for Phase 5 persistent intelligence."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "core"

REQUIRED_FILES = (
    CORE / "persistent_memory.py",
    CORE / "memory_provenance.py",
    CORE / "memory_episodic.py",
    CORE / "memory_semantic.py",
    CORE / "memory_procedural.py",
    CORE / "memory_working.py",
    CORE / "personal_model.py",
    CORE / "memory_lifecycle.py",
    CORE / "persistent_intelligence.py",
)

REQUIRED_SYMBOLS = {
    "persistent_memory.py": (
        "class PersistentMemoryRecord",
        "class PersistentMemoryKind",
        "class MemoryLifecycle",
    ),
    "memory_provenance.py": (
        "class ProvenanceRef",
        "class ProvenanceChain",
        "def validate_provenance",
    ),
    "memory_episodic.py": ("class EpisodicMemory", "class EpisodicOutcome"),
    "memory_semantic.py": ("class SemanticClaim", "class SemanticValidationStatus"),
    "memory_procedural.py": ("class ProceduralMemory", "class ProcedureStep"),
    "memory_working.py": ("class WorkingMemorySnapshot",),
    "personal_model.py": ("class PersonalModel", "class PersonalModelEntry"),
    "memory_lifecycle.py": (
        "class MemoryTransition",
        "class ConsolidationProposal",
        "def propose_semantic_consolidation",
    ),
    "persistent_intelligence.py": (
        "class PersistentMemoryRepository",
        "class PersistentIntelligenceSystem",
        "class PersistentIntelligenceCoverage",
    ),
}

FORBIDDEN_CORE_PATTERNS = (
    re.compile(r"\bdef\s+execute\s*\("),
    re.compile(r"\bauthorize\s*\("),
    re.compile(r"\brun_execution_handoff\s*\("),
    re.compile(r"\bselect_provider\b"),
    re.compile(r"\bprovider_call\s*\("),
    re.compile(r"\bsubprocess\b"),
)


def fail(message: str) -> None:
    raise SystemExit(f"Phase 5 contract: {message}")


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    for filename, symbols in REQUIRED_SYMBOLS.items():
        text = (CORE / filename).read_text(encoding="utf-8")
        for symbol in symbols:
            if symbol not in text:
                fail(f"missing required symbol: {filename}: {symbol}")

    persistent = (CORE / "persistent_intelligence.py").read_text(encoding="utf-8")
    runtime = (CORE / "runtime_kernel.py").read_text(encoding="utf-8")

    required_contract_markers = (
        "persistent_memory_records",
        "persistent_memory_provenance",
        "PersistentMemoryKind.WORKING",
        "truth_established",
        "authority_granted",
        "execution_requested",
        "provider_selected",
    )
    for marker in required_contract_markers:
        if marker not in persistent:
            fail(f"missing persistent-intelligence contract marker: {marker}")

    if "PersistentIntelligenceSystem" not in runtime:
        fail("runtime kernel is not connected to PersistentIntelligenceSystem")
    if "persistent_intelligence" not in runtime:
        fail("runtime kernel missing persistent_intelligence injection/property")

    for path in REQUIRED_FILES:
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_CORE_PATTERNS:
            if pattern.search(text):
                fail(
                    f"forbidden authority/execution/provider surface in {path.relative_to(ROOT)}: "
                    f"{pattern.pattern}"
                )

    if not re.search(r"record\.kind\s+is\s+PersistentMemoryKind\.WORKING", persistent):
        fail("working-memory durability boundary is not explicit")
    if not re.search(r"raise ValueError\(\"working memory is contextual", persistent):
        fail("working-memory persistence rejection is missing")
    if "return propose_semantic_consolidation(episodes)" not in persistent:
        fail("consolidation path must remain proposal-only")
    if "execution_authorized": False in ({}):
        pass

    print("Phase 5 contract: PASS")


if __name__ == "__main__":
    main()
