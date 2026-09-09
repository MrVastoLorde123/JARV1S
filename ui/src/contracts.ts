export type JarvisMode = 'Thinking' | 'Learning' | 'Working' | 'Monitoring' | 'Waiting' | 'Needs You';
export type CapabilityState = 'READY' | 'ONLINE' | 'CONNECTED' | 'RESTRICTED' | 'OFFLINE';
export type ChatSurface = 'CONVERSATION' | 'WORKSPACE' | 'RESEARCH' | 'PLANNING';
export type ProjectState = 'ACTIVE' | 'PAUSED' | 'WAITING' | 'IDLE' | 'COMPLETED';
export type WorkControlState = 'RUNNING' | 'PAUSED';
export type WorkspaceStatus = 'SELECTED' | 'AVAILABLE' | 'CREATING';
export type ResearchTopicState = 'ACTIVE' | 'QUEUED' | 'THOUGHT_ON';
export type PlanState = 'DRAFT' | 'READY' | 'IN_PROGRESS' | 'PAUSED' | 'COMPLETED';
export type SelfActivityKind = 'THINKING' | 'DELEGATING' | 'COMMUNICATING' | 'WAITING' | 'RESOURCE_GUARD';

export interface CapabilityContract { id: string; name: string; state: CapabilityState; detail?: string; }
export interface ActivityContract { id: string; kind?: string; title: string; detail: string; timestamp: string; }
export interface ProjectContract {
  id: string;
  name: string;
  progress?: number;
  state: ProjectState;
  workspaceId?: string;
  currentAction?: string;
  detail?: string;
}
export interface WorkspaceContract { id: string; name: string; path: string; status: WorkspaceStatus; detail: string; }
export interface ResearchTopicContract { id: string; title: string; state: ResearchTopicState; detail: string; sourceCount: number; thoughtCount: number; lastThought?: string; }
export interface PlanContract { id: string; title: string; state: PlanState; steps: string[]; currentStep?: number; automation?: string; target?: string; }
export interface ChatHistoryEntry { id: string; surface: ChatSurface; title: string; preview: string; timestamp: string; }
export interface DeviceContract { name: string; os: string; cpu: string; memory: string; gpu: string; storage: string; }
export interface ModelAssignmentContract { id: string; name: string; provider: string; role: string; state: 'ACTIVE' | 'IDLE' | 'OFFLINE'; detail: string; }
export interface WorkRuntimeContract { state: WorkControlState; detail: string; lastCommand: string; }
export interface SelfActivityContract { id: string; kind: SelfActivityKind; title: string; detail: string; timestamp: string; modelId?: string; }
export interface ResourceTelemetryContract { cpuLoad: number; memoryLoad: number; gpuLoad: number; activeModelTasks: number; concurrencyLimit: number; pressure: 'NORMAL' | 'ELEVATED' | 'HIGH'; strategy: 'SEQUENTIAL' | 'LIMITED_CONCURRENCY'; }

export interface JarvisSnapshot {
  mode: JarvisMode;
  online: boolean;
  cognitiveActivity: 'LOW' | 'MEDIUM' | 'HIGH';
  currentFocus: string;
  activeCapabilities: number;
  monitoredSources: number;
  activeWork: number;
  attentionRequired: boolean;
  attentionReason: string;
  uptime: string;
  lastStateChange: string;
  projects: ProjectContract[];
  activity: ActivityContract[];
  capabilities: CapabilityContract[];
  workRuntime: WorkRuntimeContract;
  workspaces: WorkspaceContract[];
  researchTopics: ResearchTopicContract[];
  plans: PlanContract[];
  chatHistory: ChatHistoryEntry[];
  device: DeviceContract;
  models: ModelAssignmentContract[];
  selfActivity: SelfActivityContract[];
  resources: ResourceTelemetryContract;
}

export const initialSnapshot: JarvisSnapshot = {
  mode: 'Waiting', online: true, cognitiveActivity: 'LOW', currentFocus: 'JARVIS Interface', activeCapabilities: 4, monitoredSources: 0, activeWork: 1,
  attentionRequired: false, attentionReason: 'Nothing currently requires your presence.', uptime: '00:00:00', lastStateChange: 'Now',
  workRuntime: { state: 'RUNNING', detail: 'No project is currently blocked by the runtime control.', lastCommand: 'None' },
  workspaces: [
    { id: 'jarvis', name: 'JARVIS', path: 'C:/Users/jeoop/PycharmProjects/JARV1S', status: 'SELECTED', detail: 'Primary development workspace' },
    { id: 'automation', name: 'Home Automation', path: 'C:/Workspace/HomeAutomation', status: 'AVAILABLE', detail: 'Automation and integration workspace' },
  ],
  projects: [
    { id: 'jarvis-interface', name: 'JARVIS Interface', progress: 56, state: 'ACTIVE', workspaceId: 'jarvis', currentAction: 'Evolving functional interface surfaces', detail: 'Current interface and gateway evolution.' },
    { id: 'bms', name: 'BMS integration', progress: 12, state: 'WAITING', workspaceId: 'automation', currentAction: 'Waiting for integration work', detail: 'PCVUE, PLC, and Modbus integration.' },
    { id: 'automation', name: 'Home Automation', progress: 5, state: 'IDLE', workspaceId: 'automation', detail: 'Future automation and device integration.' },
  ],
  researchTopics: [
    { id: 'ui', title: 'Unique JARVIS interface design', state: 'ACTIVE', detail: 'Explore interaction models beyond conventional dashboards.', sourceCount: 0, thoughtCount: 3, lastThought: 'The interface should feel like entering JARVIS, not opening a SaaS product.' },
    { id: 'agents', title: 'Agent memory and learning', state: 'QUEUED', detail: 'Compare useful approaches and identify architectural implications.', sourceCount: 0, thoughtCount: 0 },
    { id: 'bms', title: 'BMS automation architecture', state: 'THOUGHT_ON', detail: 'Connect research to practical PCVUE, PLC, and Modbus workflows.', sourceCount: 0, thoughtCount: 2, lastThought: 'Control and observability should remain separate boundaries.' },
  ],
  plans: [
    { id: 'interface', title: 'Evolve the living interface', state: 'IN_PROGRESS', steps: ['Specialize surfaces', 'Make Projects controllable', 'Connect real state', 'Add desktop presence'], currentStep: 2, target: 'JARVIS UI' },
    { id: 'research-monitor', title: 'Monitor a research source', state: 'DRAFT', steps: ['Define source', 'Schedule collection', 'Gather changes', 'Think on findings'], automation: 'Recurring research collection', target: 'Research' },
  ],
  chatHistory: [
    { id: 'conv-1', surface: 'CONVERSATION', title: 'JARVIS kickoff', preview: 'Discussed the next stage of JARVIS.', timestamp: 'Today' },
    { id: 'research-1', surface: 'RESEARCH', title: 'JARVIS interface research', preview: 'Explored a living interface beyond dashboard conventions.', timestamp: 'Today' },
    { id: 'plan-1', surface: 'PLANNING', title: 'Interface evolution plan', preview: 'Specialized the interface into meaningful operating systems.', timestamp: 'Recent' },
    { id: 'workspace-1', surface: 'WORKSPACE', title: 'JARVIS workspace', preview: 'Primary development workspace selected.', timestamp: 'Recent' },
  ],
  device: { name: 'JARVIS Host', os: 'Windows', cpu: 'Host CPU', memory: 'Host RAM', gpu: 'Host GPU', storage: 'Host storage' },
  models: [
    { id: 'reasoning', name: 'Local Reasoner', provider: 'Local', role: 'Reasoning / planning', state: 'ACTIVE', detail: 'Primary reasoning lane; one model task at a time by default.' },
    { id: 'coding', name: 'Coding Model', provider: 'Local', role: 'Workspace coding', state: 'IDLE', detail: 'Activated when workspace engineering is assigned.' },
    { id: 'vision', name: 'Vision Model', provider: 'Future', role: 'Visual understanding', state: 'OFFLINE', detail: 'No provider attached yet.' },
  ],
  selfActivity: [
    { id: 'self-1', kind: 'THINKING', title: 'Considering current priorities', detail: 'JARVIS is maintaining context around the interface and active projects.', timestamp: 'Now', modelId: 'reasoning' },
    { id: 'self-2', kind: 'DELEGATING', title: 'Preparing work assignment', detail: 'Task selection is being staged before a model receives work.', timestamp: 'Recent', modelId: 'reasoning' },
    { id: 'self-3', kind: 'RESOURCE_GUARD', title: 'Resource policy standing by', detail: 'Concurrency remains sequential until system pressure supports more.', timestamp: 'Recent' },
  ],
  resources: { cpuLoad: 34, memoryLoad: 41, gpuLoad: 8, activeModelTasks: 1, concurrencyLimit: 1, pressure: 'NORMAL', strategy: 'SEQUENTIAL' },
  activity: [
    { id: '1', kind: 'system', title: 'Living cockpit initialized', detail: 'Dynamic Home state is active.', timestamp: 'Now' },
    { id: '2', kind: 'architecture', title: 'MIND remains the core', detail: 'HOME is the orientation layer; MIND retains the internal world.', timestamp: 'Recent' },
  ],
  capabilities: [
    { id: 'interface', name: 'Interface', state: 'READY', detail: 'Canonical human interface boundary' },
    { id: 'filesystem', name: 'Filesystem', state: 'READY', detail: 'Workspace capability boundary' },
    { id: 'github', name: 'GitHub', state: 'CONNECTED', detail: 'Repository integration boundary' },
    { id: 'models', name: 'Models', state: 'ONLINE', detail: 'Model coordination surface' },
  ],
};
