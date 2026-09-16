from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ui" / "src" / "App.tsx"
MODEL = ROOT / "ui" / "src" / "cockpit" / "m25.ts"


def main() -> None:
    app = APP.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")

    required_app = (
        'const CONTROL_ENDPOINT = "/api/control-plane"',
        'const WORLD_ENDPOINT = "/api/world/observation"',
        'const CAPABILITY_ENDPOINT = "/api/capabilities"',
        "setInterval(refreshAll, 3000)",
        'cache: "no-store"',
        'Accept: "application/json"',
    )
    required_model = (
        'm25.live_system_state.v1',
        "LiveSystemState",
        "buildLiveSystemState",
        "isLiveStateFresh",
        "createUnknownLiveSystemState",
        '"UNAVAILABLE"',
        '"DEGRADED"',
        'maxAgeMs = 10_000',
    )

    missing = [marker for marker in required_app if marker not in app]
    missing.extend(marker for marker in required_model if marker not in model)
    if missing:
        raise SystemExit("M25 live system state contract: FAIL\nMissing:\n" + "\n".join(missing))

    print("M25 live system state contract: PASS")


if __name__ == "__main__":
    main()
