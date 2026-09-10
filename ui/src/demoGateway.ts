import type { ChatSurface, JarvisSnapshot, ProjectContract, WorkspaceContract } from './contracts';
import type { JarvisCommand, JarvisGateway, JarvisActivityEvent } from './gateway';
import { initialSnapshot } from './contracts';

let snapshot: JarvisSnapshot = structuredClone(initialSnapshot);
const listeners = new Set<(event: JarvisActivityEvent) => void>();
const startedAt = Date.now();
let sequence = 50;
let tick = 0;
let transitionTimer: number | undefined;

function nowLabel() { return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
function uptimeLabel() {
  const total = Math.floor((Date.now() - startedAt) / 1000);
  const h = Math.floor(total / 3600).toString().padStart(2, '0');
  const m = Math.floor((total % 3600) / 60).toString().padStart(2, '0');
  const s = (total % 60).toString().padStart(2, '0');
  return `${h}:${m}:${s}`;
}
function emit(title: string, detail: string, kind = 'system'): JarvisActivityEvent {
  const event = { id: `demo-${sequence++}`, kind, title, detail, timestamp: nowLabel() };
  snapshot = { ...snapshot, uptime: uptimeLabel(), lastStateChange: event.timestamp, activity: [event, ...snapshot.activity].slice(0, 6), activeWork: snapshot.projects.filter((project) => project.state === 'ACTIVE').length };
  listeners.forEach((listener) => listener(event));
  return event;
}
function self(kind: JarvisSnapshot['selfActivity'][number]['kind'], title: string, detail: string, modelId?: string) {
  snapshot = { ...snapshot, selfActivity: [{ id: `self-${sequence++}`, kind, title, detail, timestamp: nowLabel(), modelId }, ...snapshot.selfActivity].slice(0, 8) };
}
function setTransient(mode: JarvisSnapshot['mode'], focus: string, activity: JarvisSnapshot['cognitiveActivity'], attentionRequired = false) {
  snapshot = { ...snapshot, mode, currentFocus: focus, cognitiveActivity: activity, attentionRequired, attentionReason: attentionRequired ? 'A project or system state is ready for your attention.' : 'JARVIS is processing the current request.', uptime: uptimeLabel(), lastStateChange: nowLabel() };
  if (transitionTimer !== undefined) window.clearTimeout(transitionTimer);
}
function settleToWaiting(focus = 'Standing by for direction') {
  if (transitionTimer !== undefined) window.clearTimeout(transitionTimer);
  transitionTimer = window.setTimeout(() => {
    snapshot = { ...snapshot, mode: 'Waiting', cognitiveActivity: 'LOW', currentFocus: focus, attentionRequired: false, attentionReason: 'Nothing currently requires your presence.', uptime: uptimeLabel(), lastStateChange: nowLabel() };
    emit('Ready for direction', focus, 'state');
  }, 1400);
}
function refreshTelemetry() {
  tick += 1;
  const cpu = 28 + ((tick * 7) % 32);
  const memory = 38 + ((tick * 5) % 27);
  const gpu = 6 + ((tick * 3) % 18);
  const pressure = cpu > 55 || memory > 60 ? 'ELEVATED' : 'NORMAL';
  const strategy = pressure === 'ELEVATED' ? 'SEQUENTIAL' : tick % 5 === 0 ? 'LIMITED_CONCURRENCY' : 'SEQUENTIAL';
  const previousPressure = snapshot.resources.pressure;
  snapshot = {
    ...snapshot,
    uptime: uptimeLabel(),
    resources: { cpuLoad: cpu, memoryLoad: memory, gpuLoad: gpu, activeModelTasks: snapshot.mode === 'Working' ? 1 : 0, concurrencyLimit: strategy === 'LIMITED_CONCURRENCY' ? 2 : 1, pressure, strategy },
  };
  if (pressure !== previousPressure) {
    self('RESOURCE_GUARD', `Resource pressure ${pressure.toLowerCase()}`, `CPU ${cpu}% · memory ${memory}% · strategy ${strategy}.`);
    emit('Resource posture changed', `${pressure.toLowerCase()} pressure · ${strategy.toLowerCase().replace('_', ' ')} strategy.`, 'resource');
  }
}
function createProjectFromText(text: string): ProjectContract | null {
  const match = text.match(/create project\s+(.+)/i);
  if (!match) return null;
  const name = match[1].trim().replace(/[.]+$/, '');
  if (!name) return null;
  const workspace = snapshot.workspaces.find((item) => item.status === 'SELECTED') ?? snapshot.workspaces[0];
  const id = `${name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}-${Date.now()}`;
  return { id, name, progress: 0, state: 'ACTIVE', workspaceId: workspace?.id, currentAction: 'Project procedure initiated', detail: `Created from a command in ${workspace?.name ?? 'JARVIS'}.` };
}

export const demoGateway: JarvisGateway & { snapshotSync: () => JarvisSnapshot } = {
  async snapshot() { snapshot.uptime = uptimeLabel(); return structuredClone(snapshot); },
  snapshotSync() { snapshot.uptime = uptimeLabel(); return structuredClone(snapshot); },
  async submit(command: JarvisCommand) {
    const lower = command.text.toLowerCase();
    const event = emit('Command received', `JARVIS recorded: “${command.text}”`, 'command');
    if (command.surface === 'PROJECTS' && command.projectId && (lower.startsWith('pause project') || lower.startsWith('resume project'))) {
      const nextState = lower.startsWith('pause project') ? 'PAUSED' : 'ACTIVE';
      setTransient(nextState === 'PAUSED' ? 'Waiting' : 'Working', nextState === 'PAUSED' ? 'Project paused for user guidance' : 'Project resumed under current guidance', nextState === 'PAUSED' ? 'LOW' : 'HIGH', nextState === 'PAUSED');
      snapshot = { ...snapshot, projects: snapshot.projects.map((project) => project.id === command.projectId ? { ...project, state: nextState, currentAction: nextState === 'PAUSED' ? 'Paused for user guidance' : 'Resumed under current guidance' } : project), workRuntime: { state: nextState === 'PAUSED' ? 'PAUSED' : 'RUNNING', detail: nextState === 'PAUSED' ? 'The selected project is held for additional guidance.' : 'The selected project may continue under current guidance.', lastCommand: command.text } };
      self(nextState === 'PAUSED' ? 'WAITING' : 'DELEGATING', nextState === 'PAUSED' ? 'Project procedure held' : 'Project procedure resumed', nextState === 'PAUSED' ? 'JARVIS is waiting for additional guidance.' : 'JARVIS restored the project procedure under current guidance.');
      emit(nextState === 'PAUSED' ? 'Project paused' : 'Project resumed', `${command.projectId} is now ${nextState.toLowerCase()}.`, 'project');
      return event;
    }
    const createdProject = createProjectFromText(command.text);
    if (createdProject) {
      setTransient('Working', createdProject.name, 'HIGH');
      snapshot = { ...snapshot, projects: [createdProject, ...snapshot.projects] };
      self('DELEGATING', 'Project procedure initiated', `${createdProject.name} entered the active project queue.`, 'reasoning');
      emit('Project initiated', `${createdProject.name} was created and attached to the active workspace.`, 'project');
      settleToWaiting(`Project created: ${createdProject.name}`);
      return event;
    }
    const workspaceMatch = command.text.match(/select workspace directory\s+(.+)/i);
    if (workspaceMatch) {
      const name = workspaceMatch[1].trim();
      const existing = snapshot.workspaces.find((workspace) => workspace.name.toLowerCase() === name.toLowerCase());
      let selectedId = existing?.id;
      let workspaces: WorkspaceContract[] = snapshot.workspaces.map((workspace) => ({ ...workspace, status: workspace.id === existing?.id ? 'SELECTED' as const : 'AVAILABLE' as const }));
      if (!existing) { const created: WorkspaceContract = { id: `workspace-${Date.now()}`, name, path: name, status: 'SELECTED', detail: 'Directory selected from the interface.' }; selectedId = created.id; workspaces = [created, ...workspaces]; }
      snapshot = { ...snapshot, workspaces, projects: snapshot.projects.map((project) => project.id === 'jarvis-interface' ? { ...project, workspaceId: selectedId } : project), currentFocus: `Workspace: ${name}` };
      emit('Workspace selected', `The active workspace is now ${name}.`, 'workspace');
      return event;
    }
    if (command.surface === 'RESEARCH' && lower.includes('think')) {
      const active = snapshot.researchTopics.find((topic) => topic.state === 'ACTIVE') ?? snapshot.researchTopics[0];
      if (active) { setTransient('Thinking', active.title, 'HIGH'); snapshot = { ...snapshot, researchTopics: snapshot.researchTopics.map((topic) => topic.id === active.id ? { ...topic, state: 'THOUGHT_ON', thoughtCount: topic.thoughtCount + 1, lastThought: `JARVIS thought on this topic at ${nowLabel()}.` } : topic) }; self('THINKING', 'Research thought opened', `JARVIS is thinking on ${active.title}.`, 'reasoning'); emit('Research thought opened', `JARVIS is thinking on ${active.title}.`, 'research'); settleToWaiting(`Research thought recorded: ${active.title}`); }
      return event;
    }
    if (command.surface === 'PLANNING' && (lower.includes('automate') || lower.includes('schedule'))) {
      setTransient('Thinking', 'Planning automation', 'HIGH');
      self('DELEGATING', 'Automation procedure staged', 'Planning has produced a candidate procedure for future execution.');
      emit('Automation plan considered', 'The planning surface is preparing an executable automation proposal.', 'planning');
      settleToWaiting('Automation plan staged');
      return event;
    }
    setTransient('Thinking', command.text.slice(0, 72), 'HIGH');
    self('COMMUNICATING', 'Command context passed inward', 'JARVIS updated its active cognitive context from the user request.');
    emit('Cognitive cycle started', 'The request is being interpreted against current context and boundaries.', 'thinking');
    if (snapshot.workRuntime.state !== 'PAUSED') settleToWaiting('Standing by for the next meaningful transition');
    return event;
  },
  subscribe(_sessionId, onEvent) { listeners.add(onEvent); return () => listeners.delete(onEvent); },
};
const timer = window.setInterval(refreshTelemetry, 4500);
void timer;
