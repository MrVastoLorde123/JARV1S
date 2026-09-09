import type { JarvisSnapshot } from './contracts';
import type { JarvisCommand, JarvisGateway, JarvisActivityEvent } from './gateway';
import { initialSnapshot } from './contracts';

let snapshot: JarvisSnapshot = structuredClone(initialSnapshot);
const listeners = new Set<(event: JarvisActivityEvent) => void>();
const startedAt = Date.now();
let sequence = 20;
let tick = 0;

function nowLabel() { return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
function uptimeLabel() {
  const total = Math.floor((Date.now() - startedAt) / 1000);
  const h = Math.floor(total / 3600).toString().padStart(2, '0');
  const m = Math.floor((total % 3600) / 60).toString().padStart(2, '0');
  const s = (total % 60).toString().padStart(2, '0');
  return `${h}:${m}:${s}`;
}
function emit(title: string, detail: string, kind = 'system'): JarvisActivityEvent {
  const event: JarvisActivityEvent = { id: `demo-${sequence++}`, kind, title, detail, timestamp: nowLabel() };
  snapshot = { ...snapshot, uptime: uptimeLabel(), lastStateChange: event.timestamp, activity: [event, ...snapshot.activity].slice(0, 6) };
  listeners.forEach((listener) => listener(event));
  return event;
}
function refresh() {
  tick += 1;
  const phases: Array<{
    mode: JarvisSnapshot['mode'];
    activity: JarvisSnapshot['cognitiveActivity'];
    focus: string;
    caps: number;
    sources: number;
    attention: boolean;
  }> = [
    { mode: 'Monitoring', activity: 'MEDIUM', focus: 'Repository state and runtime signals', caps: 3, sources: 2, attention: false },
    { mode: 'Thinking', activity: 'HIGH', focus: 'Interface architecture and system model', caps: 3, sources: 4, attention: false },
    { mode: 'Working', activity: 'HIGH', focus: 'M27 interface evolution', caps: 4, sources: 5, attention: true },
    { mode: 'Learning', activity: 'MEDIUM', focus: 'Understanding user workflow patterns', caps: 4, sources: 3, attention: false },
    { mode: 'Waiting', activity: 'LOW', focus: 'Standing by for direction', caps: 3, sources: 1, attention: false },
  ];
  const phase = phases[tick % phases.length];
  snapshot = {
    ...snapshot,
    mode: phase.mode,
    cognitiveActivity: phase.activity,
    currentFocus: phase.focus,
    activeCapabilities: phase.caps,
    monitoredSources: phase.sources,
    attentionRequired: phase.attention,
    attentionReason: phase.attention ? 'A demo workflow is waiting for user intervention.' : 'JARVIS is progressing without requiring intervention.',
    uptime: uptimeLabel(),
    lastStateChange: nowLabel(),
    activeWork: snapshot.projects.filter((p) => p.state === 'ACTIVE').length,
  };
  emit(`System mode → ${phase.mode}`, `Cognitive activity ${phase.activity.toLowerCase()}; focus: ${phase.focus}.`, 'state');
}

snapshot.uptime = uptimeLabel();
const timer = window.setInterval(refresh, 4500);
void timer;

export const demoGateway: JarvisGateway & { snapshotSync: () => JarvisSnapshot } = {
  async snapshot() { snapshot.uptime = uptimeLabel(); return structuredClone(snapshot); },
  snapshotSync() { snapshot.uptime = uptimeLabel(); return structuredClone(snapshot); },
  async submit(command: JarvisCommand) {
    const event = emit('Command received', `JARVIS recorded: “${command.text}”`, 'command');
    snapshot = { ...snapshot, currentFocus: command.text.slice(0, 72), mode: 'Thinking', cognitiveActivity: 'HIGH', attentionRequired: false, attentionReason: 'JARVIS is processing the current request.' };
    window.setTimeout(() => emit('Response cycle complete', 'Command returned to the conversational workspace.', 'response'), 900);
    return event;
  },
  subscribe(_sessionId, onEvent) { listeners.add(onEvent); return () => listeners.delete(onEvent); },
};
