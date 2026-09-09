export type JarvisMode = 'Thinking' | 'Learning' | 'Working' | 'Monitoring' | 'Waiting' | 'Needs You';
export type CapabilityState = 'READY' | 'ONLINE' | 'CONNECTED' | 'RESTRICTED' | 'OFFLINE';
export interface CapabilityContract { id: string; name: string; state: CapabilityState; detail?: string; }
export interface ActivityContract { id: string; kind?: string; title: string; detail: string; timestamp: string; }
export interface ProjectContract { id: string; name: string; progress?: number; state: 'ACTIVE' | 'WAITING' | 'IDLE'; }
export interface JarvisSnapshot {
  mode: JarvisMode;
  online: boolean;
  cognitiveActivity: 'LOW' | 'MEDIUM' | 'HIGH';
  currentFocus: string;
  activeCapabilities: number;
  monitoredSources: number;
  activeWork: number;
  attentionRequired: number;
  uptime: string;
  lastStateChange: string;
  projects: ProjectContract[];
  activity: ActivityContract[];
  capabilities: CapabilityContract[];
}
export const initialSnapshot: JarvisSnapshot = {
  mode: 'Waiting', online: true, cognitiveActivity: 'LOW', currentFocus: 'JARVIS Interface',
  activeCapabilities: 3, monitoredSources: 0, activeWork: 1, attentionRequired: 0,
  uptime: '00:00:00', lastStateChange: 'Now',
  projects: [
    { id: 'jarvis', name: 'JARVIS Interface', progress: 48, state: 'ACTIVE' },
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
