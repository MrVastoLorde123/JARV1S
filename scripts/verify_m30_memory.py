from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src/memory/m30_memory_contract.py"
TESTS = ROOT / "src/memory/tests/test_m30_memory_contract.py"
ARCH = ROOT / "docs/architecture/memory.md"

required_markers = {
    CONTRACT: (
        "MemoryEvidenceRef",
        "MemoryRecord",
        "MemoryQuery",
        "MemoryRetrieval",
        "MemorySourceKind",
        "MemoryStatus",
        "confidence",
    ),
    TESTS: (
        "test_memory_requires_bounded_identity_and_confidence",
        "test_evidence_is_explicit_and_bounded",
        "test_retrieval_is_read_only_and_status_filtered",
        "test_memory_does_not_expose_authority",
    ),
    ARCH: (
        "Structured Memory",
        "Memory Evidence",
        "Memory Retrieval",
    ),
}

for path, markers in required_markers.items():
    if not path.exists():
        raise SystemExit(f"M30 verification failed: missing {path}")
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M30 verification failed: {path} missing {missing}")

print("M30 memory contract: PASS")
