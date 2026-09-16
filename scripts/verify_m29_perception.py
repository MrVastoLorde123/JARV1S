from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = ROOT / "src/core/perception_contract.py"
test = ROOT / "src/core/tests/test_perception_contract.py"
decision = ROOT / "docs/decisions/M29.1-perception.md"

required_contract = (
    "PerceptionDomain",
    "PerceptionAvailability",
    "PerceptionObservation",
    "PerceptionSnapshot",
    "authority_granted",
    "execution_requested",
    "observed_at",
    "provenance",
)
required_domains = ("FILESYSTEM", "PROCESSES", "NETWORK", "SERVICES", "LOGS", "HARDWARE")

for path in (contract, test, decision):
    if not path.is_file():
        raise SystemExit(f"missing required M29 file: {path}")

contract_text = contract.read_text(encoding="utf-8")
for marker in required_contract + required_domains:
    if marker not in contract_text:
        raise SystemExit(f"missing required M29 contract marker: {marker}")

if "does not grant authority" not in decision.read_text(encoding="utf-8"):
    raise SystemExit("M29 decision must explicitly separate perception from authority")

print("M29 perception contract: PASS")
