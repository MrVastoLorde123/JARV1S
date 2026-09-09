import type { ChatSurface, JarvisSnapshot, ProjectContract, WorkspaceContract } from './contracts';
import type { JarvisCommand, JarvisGateway, JarvisActivityEvent } from './gateway';
import { initialSnapshot } from './contracts';

let snapshot: JarvisSnapshot = structuredClone(initialSnapshot);
const listeners = new Set<(event: JarvisActivityEvent) => void>();
const startedAt = Date.now();
let sequence = 50;
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
  const event = { id: `demo-${sequence++}`, kind, title, detail, timestamp: nowLabel() };
  snapshot = { ...snapshot, uptime: uptimeLabel(), lastStateChange: event.timestamp, activity: [event, ...snapshot.activity].slice(0, 6), activeWork: snapshot.projects.filter((project) => project.state === 'ACTIVE').length };
  listeners.forEach((listener) => listener(event));
  return event;
}

function refresh() {
  tick += 1;
  const phases = [
    { mode: 'Monitoring' as const, activity: 'MEDIUM' as const, focus: 'Repository state and runtime signals', caps: 4, sources: 2, attention: false },
    { mode: 'Thinking' as const, activity: 'HIGH' as const, focus: 'Interface architecture and system model', caps: 4, sources: 4, attention: false },
    { mode: 'Working' as const, activity: 'HIGH' as const, focus: 'Functional interface evolution', caps: 5, sources: 5, attention: true },
    { mode: 'Learning' as const, activity: 'MEDIUM' as const, focus: 'Understanding user workflow patterns', caps: 5, sources: 3, attention: false },
    { mode: 'Waiting' as const, activity: 'LOW' as const, focus: 'Standing by for direction', caps: 4, sources: 1, attention: false },
  ];
  const phase = phases[tick % phases.length];
  const projects = snapshot.projects.map((project) => {
    if (project.state !== 'ACTIVE' || project.progress === undefined) return project;
    const progress = Math.min(100, project.progress + 1);
    return { ...project, progress, currentAction: progress >= 100 ? 'Completed' : project.currentAction };
  });
  snapshot = { ...snapshot, projects, mode: phase.mode, cognitiveActivity: phase.activity, currentFocus: phase.focus, activeCapabilities: phase.caps, monitoredSources: phase.sources, attentionRequired: phase.attention, attentionReason: phase.attention ? 'A project or system state is ready for your attention.' : 'Nothing currently requires your presence.', uptime: uptimeLabel(), lastStateChange: nowLabel() };
  emit(`System mode → ${phase.mode}`, `Cognitive activity ${phase.activity.toLowerCase()}; focus: ${phase.focus}.`, 'state');
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
      snapshot = {
        ...snapshot,
        projects: snapshot.projects.map((project) => project.id === command.projectId ? { ...project, state: nextState, currentAction: nextState === 'PAUSED' ? 'Paused for user guidance' : 'Resumed under current guidance' } : project),
        currentFocus: nextState === 'PAUSED' ? 'Project paused for user guidance' : 'Project resumed',
        mode: nextState === 'PAUSED' ? 'Waiting' : 'Working',
        cognitiveActivity: nextState === 'PAUSED' ? 'LOW' : 'HIGH',
        workRuntime: { state: nextState === 'PAUSED' ? 'PAUSED' : 'RUNNING', detail: nextState === 'PAUSED' ? 'The selected project is held for additional guidance.' : 'The selected project may continue under current guidance.', lastCommand: command.text },
      };
      return event;
    }

    const createdProject = createProjectFromText(command.text);
    if (createdProject) {
      snapshot = { ...snapshot, projects: [createdProject, ...snapshot.projects], currentFocus: createdProject.name, mode: 'Working', cognitiveActivity: 'HIGH', attentionRequired: false, attentionReason: 'The new project procedure has been initiated.' };
      emit('Project initiated', `${createdProject.name} was created and attached to the active workspace.`, 'project');
      return event;
    }

    const workspaceMatch = command.text.match(/select workspace directory\s+(.+)/i);
    if (workspaceMatch) {
      const name = workspaceMatch[1].trim();
      const existing = snapshot.workspaces.find((workspace) => workspace.name.toLowerCase() === name.toLowerCase());
      let selectedId = existing?.id;
      let workspaces: WorkspaceContract[] = snapshot.workspaces.map((workspace) => ({ ...workspace, status: workspace.id === existing?.id ? 'SELECTED' as const : 'AVAILABLE' as const }));
      if (!existing) {
        const created: WorkspaceContract = { id: `workspace-${Date.now()}`, name, path: name, status: 'SELECTED', detail: 'Directory selected from the interface.' };
        selectedId = created.id;
        workspaces = [created, ...workspaces];
      }
      snapshot = { ...snapshot, workspaces, projects: snapshot.projects.map((project) => project.id === 'jarvis-interface' ? { ...project, workspaceId: selectedId } : project), currentFocus: `Workspace: ${name}` };
      emit('Workspace selected', `The active workspace is now ${name}.`, 'workspace');
      return event;
    }

    if (command.surface === 'RESEARCH' && lower.includes('think')) {
      const active = snapshot.researchTopics.find((topic) => topic.state === 'ACTIVE') ?? snapshot.researchTopics[0];
      if (active) {
        snapshot = { ...snapshot, researchTopics: snapshot.researchTopics.map((topic) => topic.id === active.id ? { ...topic, state: 'THOUGHT_ON', thoughtCount: topic.thoughtCount + 1, lastThought: `JARVIS thought on this topic at ${nowLabel()}.` } : topic), currentFocus: active.title, mode: 'Thinking', cognitiveActivity: 'HIGH' };
        emit('Research thought opened', `JARVIS is thinking on ${active.title}.`, 'research');
      }
      return event;
    }

    if (command.surface === 'PLANNING' && (lower.includes('automate') || lower.includes('schedule'))) {
      snapshot = { ...snapshot, currentFocus: 'Planning automation', mode: 'Thinking', cognitiveActivity: 'HIGH' };
      emit('Automation plan considered', 'The planning surface is preparing an executable automation proposal.', 'planning');
      return event;
    }

    snapshot = { ...snapshot, currentFocus: command.text.slice(0, 72), mode: snapshot.workRuntime.state === 'PAUSED' ? 'Waiting' : 'Thinking', cognitiveActivity: snapshot.workRuntime.state === 'PAUSED' ? 'LOW' : 'HIGH', attentionRequired: false, attentionReason: 'JARVIS is processing the current request.' };
    if (snapshot.workRuntime.state !== 'PAUSED') window.setTimeout(() => emit('Response cycle complete', 'Command returned to the active interface surface.', 'response'), 900);
    return event;
  },
  subscribe(_sessionId, onEvent) { listeners.add(onEvent); return () => listeners.delete(onEvent); },
};

const timer = window.setInterval(refresh, 4500);
void timer;
