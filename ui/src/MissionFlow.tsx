import { useMemo } from 'react';
import type { JarvisSnapshot } from './contracts';
import { deriveMissionFlowState, type MissionStageStatus } from './missionFlowState';

interface MissionFlowProps {
  snapshot: JarvisSnapshot;
}

function statusLabel(status: MissionStageStatus): string {
  if (status === 'ACTIVE') return 'LIVE';
  if (status === 'ATTENTION') return 'USER GATE';
  if (status === 'GUARDED') return 'GUARDED';
  return 'READY';
}

export default function MissionFlow({ snapshot }: MissionFlowProps) {
  const flow = useMemo(() => deriveMissionFlowState(snapshot), [snapshot]);
  return (
    <div className="mission-flow-live" data-mission-stage={flow.stage} data-mission-status={flow.status}>
      <div className="mission-flow-state">
        <div>
          <span className="mission-flow-kicker">CURRENT OPERATION</span>
          <strong>{flow.headline}</strong>
          <small>{flow.evidence}</small>
        </div>
        <div className="mission-flow-guard">
          <span>GUARD</span>
          <b>{flow.guard}</b>
        </div>
      </div>

      <div className="mission-flow-steps" role="list" aria-label="Live mission flow">
        {flow.stages.map((stage, index) => (
          <div className="mission-flow-node" role="listitem" key={stage.id}>
            <div className={`mission-flow-step ${stage.status.toLowerCase()}`} data-stage={stage.id}>
              <span className="mission-flow-index">{String(index + 1).padStart(2, '0')}</span>
              <div>
                <b>{stage.label}</b>
                <small>{statusLabel(stage.status)} · {stage.detail}</small>
              </div>
            </div>
            {index < flow.stages.length - 1 && <div className="mission-flow-connector" aria-hidden="true"><i /></div>}
          </div>
        ))}
      </div>
    </div>
  );
}
