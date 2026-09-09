export type JarvisMode = 'Thinking' | 'Learning' | 'Working' | 'Monitoring' | 'Waiting' | 'Needs You';
export type CapabilityState = 'READY' | 'ONLINE' | 'CONNECTED' | 'RESTRICTED' | 'OFFLINE';
export type ChatSurface = 'CONVERSATION' | 'WORKSPACE' | 'RESEARCH' | 'PLANNING';
export type WorkControlState = 'RUNNING' | 'PAUSED';
export interface CapabilityContract { id: string; name: string; state: CapabilityState; detail?: string; }
export interface ActivityContract { id: string; kind?: string; title: string; detail: string; timestamp: string; }
export interface ProjectContract { id: string; name: string; progress?: number; state: 'ACTIVE' | 'WAITING' | 'IDLE'; }
export interface WorkspaceContract { id: string; name: string; path: string; status: 'SELECTED' | 'AVAILABLE' | 'CREATING'; detail: string; }
export interface ResearchTopicContract { id: string; title: string; state: 'ACTIVE' | 'QUEUED' | 'THOUGHT_ON'; detail: string; }
export interface PlanContract { id: string; title: string; state: 'DRAFT' | 'READY' | 'IN_PROGRESS' | 'PAUSED'; steps: string[]; currentStep?: number; }
export interface WorkRuntimeContract { state: WorkControlState; detail: string; lastCommand: string; }
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
}
export const initialSnapshot: JarvisSnapshot = {
  mode: 'Waiting', online: true, cognitiveActivity: 'LOW', currentFocus: 'JARVIS Interface',
  activeCapabilities: 3, monitoredSources: 0, activeWork: 1, attentionRequired: false,
  attentionReason: 'Nothing currently requires your presence.', uptime: '00:00:00', lastStateChange: 'Now',
  workRuntime: { state: 'RUNNING', detail: 'No live task is currently being controlled.', lastCommand: 'None' },
  workspaces: [
    { id: 'jarvis', name: 'JARVIS', path: 'C:/Users/jeoop/PycharmProjects/JARV1S', status: 'SELECTED', detail: 'Primary development workspace' },
    { id: 'automation', name: 'Home Automation', path: 'C:/Workspace/HomeAutomation', status: 'AVAILABLE', detail: 'Automation and integration workspace' },
  ],
  researchTopics: [
    { id: 'ui', title: 'Unique JARVIS interface design', state: 'ACTIVE', detail: 'Explore interaction models beyond conventional dashboards.' },
    { id: 'agents', title: 'Agent memory and learning', state: 'QUEUED', detail: 'Compare useful approaches and identify architectural implications.' },
    { id: 'bms', title: 'BMS automation architecture', state: 'THOUGHT_ON', detail: 'Connect research to practical PCVUE, PLC, and Modbus workflows.' },
  ],
  plans: [
    { id: 'm27', title: 'Evolve the living interface', state: 'IN_PROGRESS', steps: ['Specialize chat surfaces', 'Make work controllable', 'Connect to real state', 'Add desktop presence'], currentStep: 1 },
    { id: 'm28', title: 'Real gateway integration', state: 'DRAFT', steps: ['Define transport', 'Expose state', 'Stream events', 'Connect actions'] },
  ],
  projects: [
    { id: 'jarvis', name: 'JARVIS Interface', progress: 52, state: 'ACTIVE' },
    { id: 'bms', name: 'BMS integration', progress: 12, state: 'WAITING' },
    { id: 'automation', name: 'Home Automation', state: 'IDLE' },
  ],
  activity: [
    { id: '1', kind: 'system', title: 'Living cockpit initialized', detail: 'Dynamic Home state is active.', timestamp: 'Now' },
    { id: '2', kind: 'architecture', title: 'Gateway boundary retained', detail: 'Frontend remains provider- and authority-neutral.', timestamp: 'Recent' },
  ],
  capabilities: [
    { id: 'interface', name: 'Interface', state: 'READY', detail: 'Canonical human interface boundary' },
    { id: 'filesystem', name: 'Filesystem', state: 'READY', detail: 'Read-only capability' },
    { id: 'github', name: 'GitHub', state: 'CONNECTED', detail: 'Repository integration boundary' },
    { id: 'models', name: 'Models', state: 'OFFLINE', detail: 'No provider attached yet' },
  ],
};
