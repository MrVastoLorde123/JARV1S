import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type LandscapeId = 'OPERATIONS' | 'MIND' | 'AGENTS' | 'MODELS' | 'CAPABILITIES' | 'WORK' | 'MARKET';

const landscapes: Array<{ id: LandscapeId; title: string; detail: string }> = [
  { id: 'OPERATIONS', title: 'OPERATIONS', detail: 'missions, context, activity' },
  { id: 'MIND', title: 'MIND', detail: 'memory, learning, reasoning' },
  { id: 'AGENTS', title: 'AGENTS', detail: 'workers, delegation, handoffs' },
  { id: 'MODELS', title: 'MODELS', detail: 'intelligence lanes and providers' },
  { id: 'CAPABILITIES', title: 'CAPABILITIES', detail: 'skills, tools, permissions' },
  { id: 'WORK', title: 'WORK', detail: 'projects, workspaces, artifacts' },
  { id: 'MARKET', title: 'MARKET', detail: 'trading and external systems' },
];

function target(snapshot: JarvisSnapshot) {
  if (!snapshot.online || snapshot.mode === 'Waiting') return 'CORE';
  if (snapshot.attentionRequired || snapshot.mode === 'Needs You') return 'ATTENTION';
  if (snapshot.mode === 'Working') return 'MISSION';
  if (snapshot.mode === 'Thinking' || snapshot.mode === 'Learning') return 'CONTEXT';
  if (snapshot.mode === 'Monitoring') return 'RUNTIME';
  return 'CORE';
}

export default function JarvisLandscape() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [landscape, setLandscape] = useState<LandscapeId>('OPERATIONS');
  const [traveling, setTraveling] = useState(false);

  useEffect(() => demoGateway.subscribe('jarvis-landscape', () => setSnapshot(demoGateway.snapshotSync())), []);

  const destination = target(snapshot);
  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE');
  const mission = snapshot.projects.find((project) => project.state === 'ACTIVE') ?? snapshot.projects[0];
  const activeLandscape = useMemo(() => landscapes.find((item) => item.id === landscape)!, [landscape]);

  const moveLandscape = (next: LandscapeId) => {
    if (next === landscape) return;
    setTraveling(true);
    window.setTimeout(() => {
      setLandscape(next);
      setTraveling(false);
    }, 520);
  };

  return (
    <div className={`jarvis-landscape landscape-${landscape.toLowerCase()} target-${destination.toLowerCase()} ${traveling ? 'traveling' : ''}`}>
      <div className="landscape-topology" aria-hidden="true" />
      <div className="landscape-label">
        <span>JARVIS WORLD</span>
        <b>{activeLandscape.title}</b>
        <small>{activeLandscape.detail}</small>
      </div>

      <div className="landscape-selector" role="navigation" aria-label="JARVIS landscapes">
        {landscapes.map((item) => (
          <button key={item.id} className={item.id === landscape ? 'active' : ''} onClick={() => moveLandscape(item.id)}>
            <i />
            <span>{item.title}</span>
          </button>
        ))}
      </div>

      <div className="landscape-chart" aria-hidden="true">
        <div className="chart-ring ring-a" />
        <div className="chart-ring ring-b" />
        <div className="chart-ring ring-c" />
        <span className="chart-axis axis-h" />
        <span className="chart-axis axis-v" />

        <div className="chart-region region-mission"><span />MISSION</div>
        <div className="chart-region region-context"><span />CONTEXT</div>
        <div className="chart-region region-runtime"><span />RUNTIME</div>
        <div className="chart-region region-ability"><span />ABILITY</div>

        <div className="jarvis-presence">
          <span className="presence-trail" />
          <div className="presence-body"><i /><b>J</b></div>
          <small>{snapshot.mode}</small>
        </div>

        <div className="chart-data">
          <article><span>MISSION</span><b>{mission?.name ?? 'No active mission'}</b><small>{mission?.progress ?? 0}% · {mission?.state ?? 'IDLE'}</small></article>
          <article><span>MODEL</span><b>{activeModel?.name ?? 'No active model'}</b><small>{snapshot.resources.activeModelTasks}/{snapshot.resources.concurrencyLimit} active lanes</small></article>
          <article><span>ABILITY</span><b>{snapshot.activeCapabilities} live</b><small>{snapshot.capabilities.filter((item) => item.state !== 'OFFLINE').length} connected surfaces</small></article>
          <article><span>HISTORY</span><b>{snapshot.selfActivity.length} recent signals</b><small>world state retained</small></article>
        </div>
      </div>
    </div>
  );
}
