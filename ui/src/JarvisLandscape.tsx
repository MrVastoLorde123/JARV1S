import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import { fetchWorldObservation, type WorldObservationPayload } from './worldObservationClient';
import type { JarvisSnapshot } from './contracts';

type LandscapeId = 'OPERATIONS' | 'MIND' | 'AGENTS' | 'MODELS' | 'CAPABILITIES' | 'WORK' | 'MARKET';

const landscapes: Array<{ id: LandscapeId; title: string; detail: string }> = [
  { id: 'OPERATIONS', title: 'OPERATIONS', detail: 'command paths, navigation, active intent' },
  { id: 'MIND', title: 'MIND', detail: 'memory, knowledge, concepts, learning' },
  { id: 'AGENTS', title: 'AGENTS', detail: 'workers, delegation, movement, handoffs' },
  { id: 'MODELS', title: 'MODELS', detail: 'providers, model lanes, selection, execution' },
  { id: 'CAPABILITIES', title: 'CAPABILITIES', detail: 'skills, tools, permissions, surfaces' },
  { id: 'WORK', title: 'WORK', detail: 'projects, workspaces, artifacts, procedures' },
  { id: 'MARKET', title: 'MARKET', detail: 'signals, positions, external systems' },
];

export default function JarvisLandscape() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [world, setWorld] = useState<WorldObservationPayload | null>(null);
  const [landscape, setLandscape] = useState<LandscapeId>('OPERATIONS');
  const [traveling, setTraveling] = useState(false);

  useEffect(() => demoGateway.subscribe('jarvis-landscape', () => setSnapshot(demoGateway.snapshotSync())), []);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const result = await fetchWorldObservation();
        if (!cancelled) {
          setWorld(result.observation);
          const backendLandscape = result.observation.world.current_landscape as LandscapeId;
          if (landscapes.some((item) => item.id === backendLandscape)) setLandscape(backendLandscape);
        }
      } catch {
        if (!cancelled) setWorld(null);
      }
    };
    void load();
    const interval = window.setInterval(() => void load(), 2000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE');
  const mission = snapshot.projects.find((project) => project.state === 'ACTIVE') ?? snapshot.projects[0];
  const activeLandscape = useMemo(() => landscapes.find((item) => item.id === landscape)!, [landscape]);
  const activeAgents = world?.world.active_agent_count ?? 0;
  const agentsInLandscape = world?.world.landscape_counts?.[landscape] ?? 0;

  const moveLandscape = (next: LandscapeId) => {
    if (next === landscape) return;
    setTraveling(true);
    window.dispatchEvent(new CustomEvent<LandscapeId>('jarvis:landscape', { detail: next }));
    window.setTimeout(() => {
      setLandscape(next);
      setTraveling(false);
    }, 520);
  };

  return (
    <div className={`jarvis-landscape landscape-${landscape.toLowerCase()} target-${landscape.toLowerCase()} ${traveling ? 'traveling' : ''}`}>
      <div className="landscape-topology" aria-hidden="true" />
      <div className="landscape-label">
        <span>JARVIS WORLD / LANDSCAPE</span>
        <b>{activeLandscape.title}</b>
        <small>{activeLandscape.detail} · {agentsInLandscape} backend agents here</small>
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
          <small>{activeAgents > 0 ? `${activeAgents} AGENTS ACTIVE` : world ? 'WORLD QUIET' : 'WORLD OFFLINE'}</small>
        </div>

        <div className="chart-data">
          <article><span>MISSION</span><b>{mission?.name ?? 'No active mission'}</b><small>{mission?.progress ?? 0}% · {mission?.state ?? 'IDLE'}</small></article>
          <article><span>MODEL</span><b>{activeModel?.name ?? 'No active model'}</b><small>{snapshot.resources.activeModelTasks}/{snapshot.resources.concurrencyLimit} active lanes</small></article>
          <article><span>AGENCY</span><b>{activeAgents} live agents</b><small>{agentsInLandscape} currently in {landscape}</small></article>
          <article><span>HISTORY</span><b>{snapshot.selfActivity.length} recent signals</b><small>backend world observation is the source of agent presence</small></article>
        </div>
      </div>
    </div>
  );
}
