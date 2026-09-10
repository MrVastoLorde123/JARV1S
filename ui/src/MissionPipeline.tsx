import { useMemo } from 'react';
import type { JarvisSnapshot } from './contracts';
import { deriveMissionFlowState } from './missionFlowState';

export default function MissionPipeline({ snapshot }: { snapshot: JarvisSnapshot }) {
  const flow = useMemo(() => deriveMissionFlowState(snapshot), [snapshot]);
  return (
    <div className="mission-pipeline-live" data-mission-stage={flow.stage} data-mission-status={flow.status}>
      {flow.stages.map((stage, index) => (
        <div className="mission-pipeline-node" key={stage.id}>
          <div className={`mission-pipeline-stage ${stage.status.toLowerCase()}`}>
            <span>{index === stageOrderIndex(flow.stage) ? '●' : stage.status === 'READY' ? '·' : '●'}</span>
            <div><b>{stage.label}</b><small>{stage.status === 'ACTIVE' ? stage.detail : stage.status}</small></div>
          </div>
          {index < flow.stages.length - 1 && <div className="mission-pipeline-arrow" aria-hidden="true">→</div>}
        </div>
      ))}
    </div>
  );
}

function stageOrderIndex(stage: string): number {
  return ['OBSERVE', 'REASON', 'ASSIGN', 'EXECUTE', 'VERIFY'].indexOf(stage);
}
