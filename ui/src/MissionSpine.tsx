import { useMemo, useState } from 'react';
import type { JarvisSnapshot } from './contracts';

type Space = 'HOME' | 'CHAT' | 'WORK' | 'CONTROL' | 'MIND' | 'CAPABILITIES' | 'SELF';

interface MissionSpineProps {
  snapshot: JarvisSnapshot;
  selectedProjectId: string;
  selectedWorkspaceId: string;
  navigate: (space: Space) => void;
  onSelectProject: (id: string) => void;
  onSelectWorkspace: (id: string) => void;
}

const stageForMode: Record<JarvisSnapshot['mode'], string> = {
  Thinking: 'REASON',
  Learning: 'VERIFY',
  Working: 'EXECUTE',
  Monitoring: 'OBSERVE',
  Waiting: 'WAIT',
  'Needs You': 'ATTENTION',
};

function MissionSpine({
  snapshot,
  selectedProjectId,
  selectedWorkspaceId,
  navigate,
  onSelectProject,
  onSelectWorkspace,
}: MissionSpineProps) {
  const [traceOpen, setTraceOpen] = useState(false);
  const selectedProject = snapshot.projects.find((project) => project.id === selectedProjectId) ?? snapshot.projects[0];
  const selectedWorkspace = snapshot.workspaces.find((workspace) => workspace.id === selectedWorkspaceId) ?? snapshot.workspaces[0];
  const assignedModel = snapshot.models.find((model) => model.state === 'ACTIVE') ?? snapshot.models[0];
  const currentStage = stageForMode[snapshot.mode];
  const latestActivity = snapshot.selfActivity[0] ?? snapshot.activity[0];
  const linkedProjectCount = snapshot.projects.filter((project) => project.workspaceId === selectedWorkspace?.id).length;
  const traceItems = useMemo(() => snapshot.selfActivity.slice(0, 4), [snapshot.selfActivity]);

  return (
    <section className="mission-spine" aria-label="Current JARVIS mission context">
      <div className="mission-spine-main">
        <button className="spine-objective" onClick={() => navigate('CONTROL')} aria-label="Open mission control">
          <span className="spine-kicker">LIVE MISSION</span>
          <b>{selectedProject?.name ?? snapshot.currentFocus}</b>
          <small>{snapshot.currentFocus}</small>
        </button>

        <div className="spine-route" aria-label="Mission route">
          <button onClick={() => navigate('MIND')}><span>CONTEXT</span><b>{selectedWorkspace?.name ?? 'No workspace'}</b></button>
          <i aria-hidden="true">→</i>
          <button onClick={() => navigate('CONTROL')}><span>STAGE</span><b>{currentStage}</b></button>
          <i aria-hidden="true">→</i>
          <button onClick={() => navigate('SELF')}><span>MODEL</span><b>{assignedModel?.name ?? 'Standby'}</b></button>
        </div>

        <div className="spine-status">
          <span className={`spine-status-led spine-${snapshot.mode.toLowerCase().replace(/\s+/g, '-')}`} />
          <div><b>{snapshot.mode}</b><small>{latestActivity?.title ?? 'Awaiting a transition'}</small></div>
        </div>

        <button className="spine-trace-trigger" onClick={() => setTraceOpen((open) => !open)} aria-expanded={traceOpen}>
          <span>TRACE</span><b>{snapshot.selfActivity.length.toString().padStart(2, '0')}</b><small>{traceOpen ? 'CLOSE' : 'OPEN'}</small>
        </button>
      </div>

      <div className="mission-spine-context">
        <button onClick={() => { onSelectProject(selectedProject?.id ?? ''); navigate('WORK'); }}>
          <span>PROJECT</span><b>{selectedProject?.name ?? 'Unassigned'}</b><small>{selectedProject?.state ?? 'IDLE'} · {selectedProject?.progress ?? 0}%</small>
        </button>
        <button onClick={() => { onSelectWorkspace(selectedWorkspace?.id ?? ''); navigate('CHAT'); }}>
          <span>WORKSPACE</span><b>{selectedWorkspace?.name ?? 'Unassigned'}</b><small>{linkedProjectCount} linked work object{linkedProjectCount === 1 ? '' : 's'}</small>
        </button>
        <button onClick={() => navigate('CAPABILITIES')}>
          <span>CAPABILITY</span><b>{snapshot.activeCapabilities} READY</b><small>{snapshot.capabilities.filter((capability) => capability.state !== 'OFFLINE').length} connected surface{snapshot.capabilities.filter((capability) => capability.state !== 'OFFLINE').length === 1 ? '' : 's'}</small>
        </button>
        <button onClick={() => navigate('CONTROL')}>
          <span>AUTHORITY</span><b>CORE / POLICY</b><small>{snapshot.attentionRequired ? 'Decision attention required' : 'No pending user gate'}</small>
        </button>
      </div>

      {traceOpen && (
        <div className="mission-trace-drawer">
          <div className="trace-drawer-head"><div><span>LIVE TRACE INSPECTOR</span><b>Structured events only</b></div><button onClick={() => navigate('CONTROL')}>OPEN MISSION CONTROL →</button></div>
          <div className="trace-drawer-grid">
            {traceItems.length === 0 ? <div className="trace-empty">No trace events are currently available.</div> : traceItems.map((item, index) => (
              <div className="trace-drawer-event" key={item.id}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <div><b>{item.title}</b><p>{item.detail}</p></div>
                <time>{item.timestamp}</time>
              </div>
            ))}
          </div>
          <div className="trace-drawer-foot"><span>MODEL · {assignedModel?.name ?? 'NONE'}</span><span>STAGE · {currentStage}</span><span>RESOURCE · {snapshot.resources.strategy}</span><span>RESULT · AWAITING VERIFICATION</span></div>
        </div>
      )}
    </section>
  );
}

export default MissionSpine;
