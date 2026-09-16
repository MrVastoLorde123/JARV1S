from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ui" / "src" / "App.tsx"
MODEL = ROOT / "ui" / "src" / "cockpit" / "m24.ts"
ENTRY = ROOT / "ui" / "index.html"


def main() -> None:
    app = APP.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    entry = ENTRY.read_text(encoding="utf-8")

    required_app_markers = (
        "CONTROL",
        "MIND",
        "CAPABILITIES",
        "AUTHORITY",
        "VERIFICATION",
        "ACTIVITY",
    )
    for marker in required_app_markers:
        assert marker in app, f"missing cockpit marker: {marker}"

    for marker in (
        'M24_COCKPIT_SCHEMA = "m24.cockpit.v1"',
        "OPERATIONAL_STAGES",
        "CockpitWorkState",
        "CockpitHealth",
        "CockpitSnapshot",
        "normalizeProgress",
        "createEmptyCockpitSnapshot",
    ):
        assert marker in model, f"missing M24 contract marker: {marker}"

    assert '<div id="root"></div>' in entry
    assert '/src/main.tsx' in entry
    print("M24 cockpit contract: PASS")


if __name__ == "__main__":
    main()
