from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

app = (ROOT / "ui" / "src" / "App.tsx").read_text(encoding="utf-8")
model = (ROOT / "ui" / "src" / "cockpit" / "m26.ts").read_text(encoding="utf-8")

required_app_markers = (
    "RUNTIME ACTIVITY",
    "cursor",
    "events.length",
    "verification?.state",
    "evidence",
)
required_model_markers = (
    'M26_ACTIVITY_EVIDENCE_SCHEMA = "m26.activity_evidence.v1"',
    "CockpitActivityEvent",
    "CockpitEvidenceReference",
    "ActivityEvidenceState",
    "normalizeActivityEvent",
    "normalizeEvidenceReference",
    "normalizeActivityWindow",
    "createEmptyActivityEvidenceState",
    "UNKNOWN",
)

missing_app = [marker for marker in required_app_markers if marker not in app]
missing_model = [marker for marker in required_model_markers if marker not in model]

if missing_app or missing_model:
    if missing_app:
        print("Missing App activity/evidence markers:", ", ".join(missing_app))
    if missing_model:
        print("Missing M26 contract markers:", ", ".join(missing_model))
    raise SystemExit(1)

# M26 is observation/presentation only. Reject an accidental direct tool-command surface
# inside the new contract module itself.
for forbidden in ("fetch(", "fetch ", "WebSocket", "XMLHttpRequest", "invoke_tool", "execute_tool"):
    if forbidden in model:
        print(f"Forbidden execution surface found in M26 contract: {forbidden}")
        raise SystemExit(1)

print("M26 activity/evidence contract: PASS")
