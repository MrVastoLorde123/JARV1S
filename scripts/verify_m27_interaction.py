from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "ui" / "src" / "App.tsx"
CONTRACT = ROOT / "ui" / "src" / "cockpit" / "m27.ts"

app = APP.read_text(encoding="utf-8")
contract = CONTRACT.read_text(encoding="utf-8")

required_app_markers = [
    'const COMMAND_ENDPOINT = "/api/command";',
    'type Envelope =',
    'async function submitCommand',
    'form className="chat-composer"',
    'SEND TO JARVIS',
    'No automatic execution.',
    'X-JARVIS-Session-ID',
]
required_contract_markers = [
    'm27.interaction.v1',
    'INTERACTION_STATES',
    'InteractionRequest',
    'InteractionResponse',
    'InteractionError',
    'InteractionStateSnapshot',
    'automaticExecution: false',
    'createInteractionRequest',
    'normalizeInteractionResponse',
]

missing = [marker for marker in required_app_markers if marker not in app]
missing += [marker for marker in required_contract_markers if marker not in contract]

if missing:
    raise SystemExit("M27 interaction verification failed: " + ", ".join(missing))

if "fetch(COMMAND_ENDPOINT" not in app:
    raise SystemExit("M27 interaction verification failed: command endpoint is not invoked by the existing explicit submit path")

print("M27 interaction contract: PASS")
