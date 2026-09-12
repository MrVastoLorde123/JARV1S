import { useEffect, useState, type FormEvent } from "react";
import "./functional.css";

type WorldFrame = {
  schema?: string;
  request_id?: string;
  session_id?: string | null;
  world?: {
    generated_at?: string;
    active_agent_count?: number;
    current_landscape?: string;
    landscape_counts?: Record<string, number>;
    authority_granted?: boolean;
    permissions_granted?: boolean;
  };
  metadata?: Record<string, unknown>;
  authority_granted?: boolean;
  authorization_granted?: boolean;
  execution_requested?: boolean;
  policy_mutation?: boolean;
};

type Envelope = {
  content?: string;
  request_id?: string;
  metadata?: Record<string, unknown>;
  error?: string;
  detail?: string;
};

const WORLD_ENDPOINT = "/api/world/observation";
const COMMAND_ENDPOINT = "/api/command";

function App() {
  const [frame, setFrame] = useState<WorldFrame | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [command, setCommand] = useState("");
  const [commandResult, setCommandResult] = useState("No command has been submitted.");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      const response = await fetch(WORLD_ENDPOINT, {
        headers: {
          Accept: "application/json",
          "X-JARVIS-Session-ID": "desktop",
        },
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`World observation returned HTTP ${response.status}.`);
      }

      const envelope = (await response.json()) as Envelope;
      if (!envelope.content) {
        throw new Error("World observation response did not contain content.");
      }

      const next = JSON.parse(envelope.content) as WorldFrame;
      if (next.schema !== "m28.13.world_observation") {
        throw new Error(`Unexpected world schema: ${String(next.schema)}.`);
      }

      setFrame(next);
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unknown backend error.");
    }
  }

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 2000);
    return () => window.clearInterval(timer);
  }, []);

  const world = frame?.world;
  const online = frame !== null && error === null;
  const activeAgents = world?.active_agent_count ?? 0;
  const landscape = world?.current_landscape ?? "UNKNOWN";

  async function submitCommand(event: FormEvent) {
    event.preventDefault();
    const text = command.trim();
    if (!text || busy) return;

    setBusy(true);
    setCommandResult("Sending command to JARVIS...");

    try {
      const response = await fetch(COMMAND_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-JARVIS-Session-ID": "desktop",
        },
        body: JSON.stringify({ content: text }),
      });

      const payload = (await response.json()) as Envelope;
      if (!response.ok) {
        throw new Error(payload.detail || payload.error || `Command returned HTTP ${response.status}.`);
      }

      setCommandResult(payload.content || "JARVIS returned an empty response.");
      setCommand("");
    } catch (cause) {
      setCommandResult(cause instanceof Error ? cause.message : "Unknown command error.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="m28-shell">
      <header className="m28-header">
        <div>
          <div className="m28-kicker">JARVIS OPERATING ENVIRONMENT</div>
          <h1>JARVIS</h1>
        </div>
        <div className={`m28-status ${online ? "ready" : "offline"}`}>
          <span />
          {online ? "ONLINE" : "OFFLINE"}
        </div>
      </header>

      <main className="m28-main">
        <section className="m28-panel m28-state">
          <div className="m28-panel-label">CURRENT STATE</div>
          <div className="m28-state-value">{online ? "OBSERVING" : "UNAVAILABLE"}</div>
          <div className="m28-focus">{landscape}</div>

          <div className="m28-metrics">
            <Metric label="ACTIVE AGENTS" value={activeAgents} />
            <Metric label="LANDSCAPE" value={landscape} />
            <Metric label="AUTHORITY" value={world?.authority_granted ? "GRANTED" : "NOT GRANTED"} />
            <Metric label="EXECUTION" value={"BACKEND OWNED"} />
          </div>
        </section>

        <section className="m28-panel">
          <div className="m28-panel-label">LAST OBSERVATION</div>
          <div className="m28-event-title">
            {error ?? (frame ? "M28.13 world observation received." : "Waiting for backend observation.")}
          </div>
          <div className="m28-event-meta">Generated: {world?.generated_at ?? "UNAVAILABLE"}</div>
          <div className="m28-event-meta">Request: {frame?.request_id ?? "UNAVAILABLE"}</div>
        </section>

        <section className="m28-panel">
          <div className="m28-panel-label">COMMAND</div>
          <form className="m28-command" onSubmit={submitCommand}>
            <input
              value={command}
              onChange={(event) => setCommand(event.target.value)}
              placeholder="Tell JARVIS what you want to do..."
              aria-label="JARVIS command"
              disabled={busy}
            />
            <button type="submit" disabled={!command.trim() || busy}>
              {busy ? "RUNNING" : "SEND"}
            </button>
          </form>
          <pre className="m28-command-result">{commandResult}</pre>
        </section>

        <section className="m28-panel">
          <div className="m28-panel-label">CAPABILITY SURFACE</div>
          <Capability name="World observation" state={online ? "READY" : "UNAVAILABLE"} />
          <Capability name="UI command → JARVIS runtime" state="READY" />
          <Capability name="Tool execution" state="BACKEND OWNED" />
          <Capability name="Filesystem mutation" state="NOT VERIFIED" />
          <Capability name="Coding-agent delegation" state="NOT VERIFIED" />
          <Capability name="Independent verification" state="NOT VERIFIED" />
        </section>
      </main>

      <footer className="m28-footer">
        <span>M28</span>
        <span>MINIMAL TRUTHFUL SHELL</span>
        <span>{online ? "BACKEND CONNECTED" : "BACKEND DISCONNECTED"}</span>
      </footer>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="m28-metric">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function Capability({ name, state }: { name: string; state: string }) {
  const ready = state === "READY";
  return (
    <div className="m28-capability">
      <span className={`m28-capability-dot ${ready ? "ready" : "muted"}`} />
      <span>{name}</span>
      <b>{state}</b>
    </div>
  );
}

export default App;
