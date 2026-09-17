"""Static contract verifier for Phase 3 Systems Intelligence."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ROOT / "src" / "core" / "capability_graph.py": (
        "CapabilityGraph",
        "CapabilityRelation",
        "CapabilityRelationKind",
    ),
    ROOT / "src" / "core" / "capability_dependency.py": (
        "CapabilityDependencyModel",
        "transitive_dependencies",
        "dependency cycle detected",
    ),
    ROOT / "src" / "core" / "capability_utility.py": (
        "CapabilityUtilityProfile",
        "CapabilityUtilityWeights",
        "utility_score",
    ),
    ROOT / "src" / "core" / "capability_composition.py": (
        "CapabilityComposition",
        "CapabilityCompositionModel",
        "assess_readiness",
    ),
    ROOT / "src" / "core" / "capability_compounding.py": (
        "CapabilityCompoundingLink",
        "CapabilityCompoundingModel",
        "weighted_gain",
    ),
    ROOT / "src" / "core" / "capability_system.py": (
        "CapabilitySystem",
        "CapabilitySystemAssessment",
        "assess_all",
    ),
    ROOT / "src" / "core" / "runtime_kernel.py": (
        "CapabilitySystem",
        "capability_system:",
        "def capability_system",
    ),
}

FORBIDDEN = (
    "authorize(",
    "run_execution_handoff(",
    "execute(",
    "invoke(",
    "select_provider",
    "select_tool",
    "provider_call",
    "subprocess",
    "open(",
    "write_text(",
    "unlink(",
)

for target, required_markers in TARGETS.items():
    if not target.exists():
        raise SystemExit(f"Phase 3 contract: missing {target}")
    text = target.read_text(encoding="utf-8")
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        raise SystemExit(f"Phase 3 contract: {target.name} missing markers {missing}")
    forbidden = [item for item in FORBIDDEN if item in text]
    if forbidden:
        raise SystemExit(f"Phase 3 contract: {target.name} contains forbidden surfaces {forbidden}")

runtime_text = (ROOT / "src" / "core" / "runtime_kernel.py").read_text(encoding="utf-8")
for marker in (
    "def authorizes_execution(self) -> bool:",
    "def executes_capability(self) -> bool:",
    "return False",
):
    if marker not in runtime_text:
        raise SystemExit(f"Phase 3 contract: runtime authority marker missing {marker}")

print("Phase 3 systems-intelligence contract: PASS")
