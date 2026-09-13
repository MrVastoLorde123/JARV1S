import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import "./functional.css";
import "./space-identity-m27.33.css";

type WorldFrame = {
  schema?: string;
  request_id?: string;
  session_id?: string | null;
  world?: {
    generated_at?: string;
    active_agent_count?: number;
    current_landscape?: string;
    authority_granted?: boolean;
    permissions_granted?: boolean;
  };
};

type Envelope = { content?: string; request_id?: string; error?: string; detail?: string };
type Capability = { name: string; description: string; version: string; risk_level: string; requires_confirmation: boolean };
type CapabilityFrame = { schema?: string; capabilities?: Capability[] };
type ServiceState = "READY" | "UNAVAILABLE" | "UNKNOWN";
type Space = "CHAT" | "CONTROL" | "MIND" | "CAPABILITIES";

const WORLD_ENDPOINT = "/api/world/observation";
const COMMAND_ENDPOINT = "/api/command";
const CAPABILITY_ENDPOINT = "/api/capabilities";
const WORLD_SCHEMA = "m28.13.world_observation";
const CAPABILITY_SCHEMA = "m28.capabilities.v1";

function App() {
  const [activeSpace, setActiveSpace] = useState<Space>("CHAT");
  const [frame, setFrame] = useState<WorldFrame | null>(null);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [worldState, setWorldState] = useState<ServiceState>("UNKNOWN");
  const [capabilityState, setCapabilityState] = useState<ServiceState>("UNKNOWN");
  const [worldError, setWorldError] = useState<string | null>(null);
  const [capabilityError, setCapabilityError] = useState<string | null>(null);
  const [command, setCommand] = useState("");
  const [commandResult, setCommandResult] = useState("No command has been submitted.");
  const [commandState, setCommandState] = useState<ServiceState>("UNKNOWN");
  const [busy, setBusy] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const refreshWorld = useCallback(async () => {
    try {
      const response = await fetch(WORLD_ENDPOINT, { headers: { Accept: "application/json", "X-JARVIS-Session-ID": "desktop" }, cache: "no-store" });
      if (!response.ok) throw new Error(`World observation returned HTTP ${response.status}.`);
      const envelope = (await response.json()) as Envelope;
      if (!envelope.content) throw new Error("World observation response did not contain content.");
      let next: WorldFrame;
      try { next = JSON.parse(envelope.content) as WorldFrame; } catch { throw new Error("World observation returned invalid JSON content."); }
      if (next.schema !== WORLD_SCHEMA) throw new Error(`Unexpected world schema: ${String(next.schema)}.`);
      setFrame(next); setWorldState("READY"); setWorldError(null); setLastRefresh(new Date());
    } catch (cause) {
      setWorldState("UNAVAILABLE");
      setWorldError(cause instanceof Error ? cause.message : "Unknown world-service error.");
    }
  }, []);

  const refreshCapabilities = useCallback(async () => {
    try {
      const response = await fetch(CAPABILITY_ENDPOINT, { headers: { Accept: "application/json" }, cache: "no-store" });
      const payload = (await response.json()) as CapabilityFrame;
      if (!response.ok) throw new Error(`Capability catalog returned HTTP ${response.status}.`);
      if (payload.schema !== CAPABILITY_SCHEMA) throw new Error(`Unexpected capability schema: ${String(payload.schema)}.`);
      setCapabilities(Array.isArray(payload.capabilities) ? payload.capabilities : []);
      setCapabilityState("READY"); setCapabilityError(null);
    } catch (cause) {
      setCapabilityState("UNAVAILABLE");
      setCapabilityError(cause instanceof Error ? cause.message : "Capability catalog unavailable.");
    }
  }, []);

  const refreshAll = useCallback(() => { void Promise.allSettled([refreshWorld(), refreshCapabilities()]); }, [refreshCapabilities, refreshWorld]);

  useEffect(() => {
    refreshAll();
    const timer = window.setInterval(refreshAll, 5000);
    return () => window.clearInterval(timer);
  }, [refreshAll]);

  const world = frame?.world;
  const explicitAuthority = world?.authority_granted === true;
  const explicitPermissions = world?.permissions_granted === true;
  const landscape = world?.current_landscape ?? "UNKNOWN";
  const activeAgents = world?.active_agent_count ?? 0;
  const shellReady = worldState === "READY" || capabilityState === "READY";
  const serviceRows = useMemo(() => [
    { name: "WORLD", state: worldState, detail: worldError },
    { name: "CAPABILITIES", state: capabilityState, detail: capabilityError },
    { name: "COMMAND", state: commandState, detail: commandState === "UNAVAILABLE" ? commandResult : null },
  ], [capabilityError, capabilityState, commandResult, commandState, worldError, worldState]);

  async function submitCommand(event: FormEvent) {
    event.preventDefault();
    const text = command.trim();
    if (!text || busy) return;
    setBusy(true); setCommandState("UNKNOWN"); setCommandResult("Sending command to JARVIS…");
    try {
      const response = await fetch(COMMAND_ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json", "X-JARVIS-Session-ID": "desktop" }, body: JSON.stringify({ content: text }) });
      let payload: Envelope = {};
      try { payload = (await response.json()) as Envelope; } catch { payload = {}; }
      if (!response.ok) throw new Error(payload.detail || payload.error || `Command returned HTTP ${response.status}.`);
      setCommandState("READY"); setCommandResult(payload.content || "JARVIS returned an empty response."); setCommand("");
    } catch (cause) {
      setCommandState("UNAVAILABLE"); setCommandResult(cause instanceof Error ? cause.message : "Unknown command error.");
    } finally { setBusy(false); }
  }

  return (
    <div className="jarvis-shell">
      <header className="topbar">
        <div className="brand-lockup"><span className="brand-mark" aria-hidden="true">J</span><div><div className="eyebrow">JARVIS OPERATING ENVIRONMENT</div><h1>JARVIS</h1></div></div>
        <div className="topbar-meta"><StatusPill label="SHELL" state={shellReady ? "READY" : "UNAVAILABLE"} /><button className="refresh-button" type="button" onClick={refreshAll}>REFRESH</button></div>
      </header>

      <div className="space-bar" role="tablist" aria-label="JARVIS spaces">
        {(["CHAT", "CONTROL", "MIND", "CAPABILITIES"] as Space[]).map((space) => (
          <button className={`space-tab ${activeSpace === space ? "active" : ""}`} key={space} type="button" role="tab" aria-selected={activeSpace === space} onClick={() => setActiveSpace(space)}>
            <span>{space}</span><small>{spaceSubtitle(space)}</small>
          </button>
        ))}
      </div>

      <main className="workspace">
        <aside className="side-panel">
          <section className="panel quiet-panel"><div className="panel-label">RUNTIME</div><div className="runtime-state">{shellReady ? "PARTIAL" : "DEGRADED"}</div><div className="runtime-note">The interface remains usable while individual backend services fail.</div></section>
          <section className="panel"><div className="panel-label">SERVICES</div><div className="service-list">{serviceRows.map((service) => <div className="service-row" key={service.name}><StatusDot state={service.state} /><div className="service-copy"><strong>{service.name}</strong><span>{service.detail ?? service.state}</span></div></div>)}</div></section>
          <section className="panel authority-panel"><div className="panel-label">AUTHORITY</div><TruthRow label="Authority granted" value={explicitAuthority ? "TRUE" : "FALSE"} /><TruthRow label="Permissions granted" value={explicitPermissions ? "TRUE" : "FALSE"} /><div className="authority-note">Connectivity and capability presence never imply authority.</div></section>
        </aside>

        <section className={`panel space-panel ${activeSpace === "CHAT" ? "chat-shell" : ""}`}>
          {activeSpace === "CHAT" && <ChatSpace command={command} busy={busy} result={commandResult} commandState={commandState} onCommandChange={setCommand} onSubmit={submitCommand} />}
          {activeSpace === "CONTROL" && <ControlSpace world={world} explicitAuthority={explicitAuthority} explicitPermissions={explicitPermissions} capabilities={capabilities} />}
          {activeSpace === "MIND" && <MindSpace frame={frame} landscape={landscape} activeAgents={activeAgents} lastRefresh={lastRefresh} worldError={worldError} />}
          {activeSpace === "CAPABILITIES" && <CapabilitiesSpace capabilities={capabilities} error={capabilityError} />}
        </section>
      </main>

      <footer className="footer-bar"><span>POST-M52 INTERFACE</span><span>OBSERVATION ≠ AUTHORITY</span><span>{lastRefresh ? `UPDATED ${lastRefresh.toLocaleTimeString()}` : "WAITING FOR OBSERVATION"}</span></footer>
    </div>
  );
}

function ChatSpace({ command, busy, result, commandState, onCommandChange, onSubmit }: { command: string; busy: boolean; result: string; commandState: ServiceState; onCommandChange: (value: string) => void; onSubmit: (event: FormEvent) => void; }) {
  return <div className="space-content chat-main"><div className="space-heading"><div><div className="panel-label">CHAT</div><h2>Tell JARVIS what you need.</h2><p>Conversation is the intent surface. Sending is always explicit.</p></div><StatusPill label="COMMAND" state={commandState} /></div>
    <form className="chat-composer" onSubmit={onSubmit}><textarea value={command} onChange={(event) => onCommandChange(event.target.value)} placeholder="Ask JARVIS to inspect, explain, plan, or act…" aria-label="JARVIS command" rows={5} disabled={busy} /><div className="composer-footer"><span>{busy ? "JARVIS is processing the explicit request." : "No automatic execution."}</span><button className="primary-button chat-orchestrate" type="submit" disabled={!command.trim() || busy}>{busy ? "RUNNING" : "SEND TO JARVIS"}</button></div></form>
    <section className="result-card"><div className="panel-label">LATEST RESPONSE</div><pre>{result}</pre></section></div>;
}

function ControlSpace({ world, explicitAuthority, explicitPermissions, capabilities }: { world: WorldFrame["world"]; explicitAuthority: boolean; explicitPermissions: boolean; capabilities: Capability[]; }) {
  return <div className="space-content mission-control"><div className="space-heading"><div><div className="panel-label">CONTROL</div><h2>Authority and execution state.</h2><p>This space exposes backend facts. It does not create permission.</p></div><StatusPill label="AUTHORITY" state={explicitAuthority ? "READY" : "UNAVAILABLE"} /></div>
    <div className="pipeline-grid"><BoundaryCard label="AUTHORITY" value={explicitAuthority ? "GRANTED" : "NOT GRANTED"} /><BoundaryCard label="PERMISSIONS" value={explicitPermissions ? "GRANTED" : "NOT GRANTED"} /><BoundaryCard label="AGENTS" value={String(world?.active_agent_count ?? 0)} /><BoundaryCard label="CAPABILITIES" value={String(capabilities.length)} /></div>
    <div className="control-note"><strong>Boundary:</strong> capability discovery, network connectivity, and UI state are not authority.</div></div>;
}

function MindSpace({ frame, landscape, activeAgents, lastRefresh, worldError }: { frame: WorldFrame | null; landscape: string; activeAgents: number; lastRefresh: Date | null; worldError: string | null; }) {
  return <div className="space-content mind-core-panel"><div className="space-heading"><div><div className="panel-label">MIND</div><h2>World and context.</h2><p>Quiet state, lineage, and observation details.</p></div><StatusPill label="WORLD" state={frame && !worldError ? "READY" : "UNAVAILABLE"} /></div>
    <div className="mind-grid"><BoundaryCard label="LANDSCAPE" value={landscape} /><BoundaryCard label="ACTIVE AGENTS" value={String(activeAgents)} /><BoundaryCard label="SESSION" value={frame?.session_id ?? "desktop"} /><BoundaryCard label="REQUEST" value={frame?.request_id ?? "UNAVAILABLE"} /></div>
    <div className="mind-context-banner"><div className="panel-label">LAST WORLD OBSERVATION</div><p>{worldError ?? "World observation is being treated as observation, not authority."}</p><span>{lastRefresh ? lastRefresh.toLocaleString() : "No successful observation yet."}</span></div></div>;
}

function CapabilitiesSpace({ capabilities, error }: { capabilities: Capability[]; error: string | null }) {
  return <div className="space-content"><div className="space-heading"><div><div className="panel-label">CAPABILITIES</div><h2>Available backend fabric.</h2><p>Inventory is informational. A capability does not become execution authority merely by being listed.</p></div><StatusPill label="CATALOG" state={error ? "UNAVAILABLE" : "READY"} /></div>
    {error ? <div className="empty-state"><strong>Capability catalog unavailable.</strong><span>{error}</span></div> : capabilities.length === 0 ? <div className="empty-state"><strong>No capabilities reported.</strong><span>The backend has not exposed any capability records.</span></div> : <div className="capability-grid">{capabilities.map((capability) => <article className="capability-card" key={capability.name}><div className="capability-header"><span className={`state-dot ${capability.requires_confirmation ? "offline" : "online"}`} /><strong>{capability.name}</strong><span>{capability.version}</span></div><p>{capability.description}</p><footer><span>{capability.risk_level.toUpperCase()}</span><span>{capability.requires_confirmation ? "CONFIRMATION" : "DIRECT"}</span></footer></article>)}</div>}</div>;
}

function BoundaryCard({ label, value }: { label: string; value: string }) { return <div className="pipeline-card"><span>{label}</span><strong>{value}</strong></div>; }
function TruthRow({ label, value }: { label: string; value: string }) { return <div className="truth-row"><span>{label}</span><strong>{value}</strong></div>; }
function StatusDot({ state }: { state: ServiceState }) { return <span className={`status-dot status-${state.toLowerCase()}`} aria-hidden="true" />; }
function StatusPill({ label, state }: { label: string; state: ServiceState }) { return <div className={`status-pill status-pill-${state.toLowerCase()}`}><StatusDot state={state} /><span>{label}</span><b>{state}</b></div>; }
function spaceSubtitle(space: Space) { switch (space) { case "CHAT": return "INTENT"; case "CONTROL": return "AUTHORITY"; case "MIND": return "CONTEXT"; case "CAPABILITIES": return "FABRIC"; } }

export default App;
