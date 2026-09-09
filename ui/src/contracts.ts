export type JarvisMode = 'Thinking' | 'Learning' | 'Working' | 'Monitoring' | 'Waiting' | 'Needs You';

export type CapabilityState = 'READY' | 'ONLINE' | 'CONNECTED' | 'RESTRICTED' | 'OFFLINE';

export interface CapabilityContract {
  id: string;
  name: string;
  state: CapabilityState;
  detail?: string;
}

export interface ActivityContract {
  id: string;
  title: string;
  detail: string;
  timestamp: string;
}

export interface ProjectContract {
  id: string;
  name: string;
  progress?: number;
  state: 'ACTIVE' | 'WAITING' | 'IDLE';
}

export interface JarvisSnapshot {
  mode: JarvisMode;
  online: boolean;
  cognitiveActivity: 'LOW' | 'MEDIUM' | 'HIGH';
  currentFocus: string;
  activeCapabilities: number;
  monitoredSources: number;
  projects: ProjectContract[];
  activity: ActivityContract[];
  capabilities: CapabilityContract[];
}

export const initialSnapshot: JarvisSnapshot = {
  mode: 'Waiting',
  online: true,
  cognitiveActivity: 'LOW',
  currentFocus: 'JARVIS Interface',
  activeCapabilities: 1,
  monitoredSources: 0,
  projects: [
    { id: 'jarvis', name: 'JARVIS Interface', progress: 28, state: 'ACTIVE' },
    { id: 'bms', name: 'BMS integration', state: 'WAITING' },
    { id: 'automation', name: 'Home Automation', state: 'IDLE' },
  ],
  activity: [
    { id: '1', title: 'Interface direction established', detail: 'HOME / WORK / MIND / CAPABILITIES / SELF', timestamp: 'Now' },
    { id: '2', title: 'V1 authority pipeline sealed', detail: 'Core boundaries remain backend-owned', timestamp: 'Recent' },
  ],
  capabilities: [
    { id: 'terminal', name: 'Interface', state: 'READY', detail: 'Canonical interface boundary' },
    { id: 'read-file', name: 'Filesystem', state: 'READY', detail: 'Read-only capability' },
    { id: 'models', name: 'Models', state: 'OFFLINE', detail: 'No provider attached yet' },
  ],
};