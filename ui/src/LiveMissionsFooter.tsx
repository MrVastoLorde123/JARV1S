import type { JarvisSnapshot } from './contracts';
import { deriveMissionFlowState } from './missionFlowState';

type Space = 'HOME' | 'CHAT' | 'WORK' | 'CONTROL' | 'MIND' | 'CAPABILITIES' | 'SELF';

interface LiveMissionsFooterProps {
  snapshot: JarvisSnapshot;
  selectedProjectId: string;
  onSelectProject: (id: string) => void;
  navigate: (space: Space) => void;
}

function LiveMissionsFooter({ snapshot, selectedProjectId, onSelectProject, navigate }: LiveMissionsFooterProps) {
  const ranked = [...snapshot.projects]
    .filter((project) => project.state === 'ACTIVE' || project.state === 'PAUSED' || project.state === 'WAITING')
    .sort((a, b) => {
      const score = (state: typeof a.state) => state === 'ACTIVE' ? 0 : state === 'PAUSED' ? 1 : 2;
      return score(a.state) - score(b.state);
    });
  const visible = ranked.slice(0, 4);
  const selected = snapshot.projects.find((project) => project.id === selectedProjectId) ?? visible[0];
  const mission = selected ? deriveMissionFlowState(snapshot, selected.id) : null;
  const activeCount = snapshot.projects.filter((project) => project.state === 'ACTIVE').length;

  return (
    <aside className="live-missions-footer" aria-label="Live missions">
      <div className="live-missions-label">
        <span className="live-missions-led" />
        <div>
          <b>LIVE MISSIONS</b>
          <small>{activeCount} ACTIVE · {snapshot.projects.length} TOTAL</small>
        </div>
      </div>
      <div className="live-missions-lanes">
        {visible.length === 0 ? (
          <button className="live-mission-empty" onClick={() => navigate('WORK')}>No active work · Open Projects →</button>
        ) : visible.map((project) => {
          const flow = deriveMissionFlowState(snapshot, project.id);
          return (
            <button
              key={project.id}
              className={`live-mission-lane ${project.id === selected?.id ? 'selected' : ''} status-${project.state.toLowerCase()}`}
              onClick={() => onSelectProject(project.id)}
              aria-label={`Select mission ${project.name}`}
            >
              <span className="live-mission-state" />
              <span className="live-mission-copy">
                <b>{project.name}</b>
                <small>{flow.stage} · {flow.modelName ?? 'STANDBY'}</small>
              </span>
              <span className="live-mission-progress">{project.progress ?? 0}%</span>
            </button>
          );
        })}
      </div>
      <button className="live-missions-focus" onClick={() => navigate('CONTROL')}>
        <span>FOCUS</span>
        <b>{selected?.name ?? snapshot.currentFocus}</b>
        <small>{mission?.transition ?? 'Awaiting mission transition'}</small>
      </button>
    </aside>
  );
}

export default LiveMissionsFooter;
