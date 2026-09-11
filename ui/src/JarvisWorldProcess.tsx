import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type LandscapeId = 'OPERATIONS' | 'MIND' | 'AGENTS' | 'MODELS' | 'CAPABILITIES' | 'WORK' | 'MARKET';
type JourneyPhase = 'PLAN' | 'DELEGATE' | 'DISCOVER' | 'EXECUTE' | 'ASSIMILATE' | 'RETURN';

const phases: Array<{ id: JourneyPhase; title: string; detail: string }> = [
  { id: 'PLAN', title: 'PLAN', detail: 'understand intent and choose a route' },
  { id: 'DELEGATE', title: 'DELEGATE', detail: 'instantiate the worker and assign responsibility' },
  { id: 'DISCOVER', title: 'DISCOVER', detail: 'gather evidence, sources, constraints' },
  { id: 'EXECUTE', title: 'EXECUTE', detail: 'perform the selected operation' },
  { id: 'ASSIMILATE', title: 'ASSIMILATE', detail: 'connect findings to JARVIS memory' },
  { id: 'RETURN', title: 'RETURN', detail: 'bring results back into the active world' },
];

function phaseFor(snapshot: JarvisSnapshot, landscape: LandscapeId): JourneyPhase {
  if (!snapshot.online) return 'PLAN';
  if (landscape === 'AGENTS') return snapshot.mode === 'Working' ? 'EXECUTE' : 'DELEGATE';
  if (landscape === 'MODELS') return snapshot.mode === 'Thinking' ? 'DISCOVER' : 'EXECUTE';
  if (landscape === 'MIND') return snapshot.mode === 'Learning' ? 'ASSIMILATE' : 'DISCOVER';
  if (landscape === 'WORK') return 'EXECUTE';
  if (landscape === 'CAPABILITIES') return 'DELEGATE';
  if (snapshot.mode === 'Working') return 'EXECUTE';
  if (snapshot.mode === 'Thinking') return 'PLAN';
  return 'RETURN';
}

function eventDetail(snapshot: JarvisSnapshot, phase: JourneyPhase) {
  const recent = snapshot.selfActivity[0];
  if (phase === 'PLAN') return recent?.detail ?? 'JARVIS is shaping a route from the current request and context.';
  if (phase === 'DELEGATE') return recent?.title ?? 'A worker boundary is being prepared.';
  if (phase === 'DISCOVER') return snapshot.researchTopics[0]?.detail ?? 'Sources and evidence are being gathered.';
  if (phase === 'EXECUTE') return snapshot.currentFocus;
  if (phase === 'ASSIMILATE') return snapshot.researchTopics.find((topic) => topic.state === 'THOUGHT_ON')?.lastThought ?? 'New findings are being connected to existing knowledge.';
  return recent?.detail ?? 'Results are being returned to the active JARVIS context.';
}

function useLandscape() {
  const [landscape, setLandscape] = useState<LandscapeId>('OPERATIONS');
  useEffect(() => {
    const handler = (event: Event) => {
      const next = (event as CustomEvent<LandscapeId>).detail;
      if (next) setLandscape(next);
    };
    window.addEventListener('jarvis:landscape', handler);
    return () => window.removeEventListener('jarvis:landscape', handler);
  }, []);
  return landscape;
}

export default function JarvisWorldProcess() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [logsOpen, setLogsOpen] = useState(false);
  const landscape = useLandscape();

  useEffect(() => demoGateway.subscribe('jarvis-process', () => setSnapshot(demoGateway.snapshotSync())), []);

  const phase = phaseFor(snapshot, landscape);
  const phaseIndex = phases.findIndex((item) => item.id === phase);
  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE');
  const activeProject = snapshot.projects.find((project) => project.state === 'ACTIVE');
  const latest = snapshot.activity.slice(0, 4);
  const knowledgeNodes = snapshot.researchTopics.flatMap((topic) => [topic.title, `${topic.sourceCount} sources`, `${topic.thoughtCount} thoughts`]);
  const sieveCount = Math.max(1, snapshot.researchTopics.reduce((sum, topic) => sum + topic.sourceCount, 0));
  const accepted = Math.max(1, snapshot.researchTopics.reduce((sum, topic) => sum + topic.thoughtCount, 0));

  const workerRoute = useMemo(() => ['JARVIS', 'AGENTS', 'MODELS', 'WORK', 'MIND', 'JARVIS'], []);

  return (
    <section className={`jarvis-process-world process-${landscape.toLowerCase()}`} aria-label="JARVIS execution world">
      <div className="process-horizon" aria-hidden="true" />

      <div className="process-presence" aria-hidden="true">
        <div className="process-j-ghost"><b>J</b><span /></div>
        <div className="process-orbit orbit-one" />
        <div className="process-orbit orbit-two" />
      </div>

      <div className="process-header">
        <span>JARVIS / LIVE PROCESS</span>
        <b>{snapshot.currentFocus}</b>
        <small>{snapshot.mode} · {snapshot.cognitiveActivity} cognitive activity</small>
      </div>

      <div className="process-journey" aria-label="Execution phases">
        {phases.map((item, index) => {
          const state = index < phaseIndex ? 'done' : index === phaseIndex ? 'active' : 'future';
          return (
            <div key={item.id} className={`journey-phase ${state}`}>
              <span className="phase-node">{index + 1}</span>
              <div><b>{item.title}</b><small>{item.detail}</small></div>
            </div>
          );
        })}
      </div>

      <div className="process-body">
        <article className="process-stream">
          <header><span>PROCESS STREAM</span><b>{phase}</b></header>
          <div className="stream-route">
            {workerRoute.map((stop, index) => (
              <div key={`${stop}-${index}`} className={`stream-stop stop-${index}`}>
                <i />
                <strong>{stop}</strong>
                {index < workerRoute.length - 1 && <span className="stream-link" />}
              </div>
            ))}
          </div>
          <div className="stream-statement">
            <b>{phase === 'DELEGATE' ? 'Researcher-07 is being created.' : phase === 'EXECUTE' ? 'A worker is operating inside the selected environment.' : phase === 'ASSIMILATE' ? 'JARVIS is absorbing the result into the knowledge field.' : 'JARVIS is moving the work through its current boundary.'}</b>
            <p>{eventDetail(snapshot, phase)}</p>
          </div>
        </article>

        <article className="process-agent-card">
          <header><span>VISIBLE WORKER</span><b>Researcher-07</b></header>
          <div className="agent-figure">
            <div className="agent-core"><i /><b>07</b></div>
            <div className="agent-route">
              <span>spawn</span><span>travel</span><span>model</span><span>return</span>
            </div>
          </div>
          <p>Scoped worker · research responsibility · result handoff</p>
        </article>

        <article className="process-sieve-card">
          <header><span>SIEVE / THROUGHPUT</span><b>{accepted}/{sieveCount + accepted}</b></header>
          <div className="sieve-funnel"><i /><i /><i /><i /><b /></div>
          <div className="sieve-meta"><span>inputs {sieveCount}</span><span>linked {accepted}</span><span>kept {Math.max(1, Math.round(accepted * 0.72))}</span></div>
        </article>

        <article className="process-map-card">
          <header><span>COGNITIVE STRUCTURE</span><b>{knowledgeNodes.length} visible nodes</b></header>
          <div className="mind-map">
            <div className="map-root"><b>JARVIS</b><small>{snapshot.currentFocus}</small></div>
            {knowledgeNodes.slice(0, 9).map((node, index) => (
              <div key={`${node}-${index}`} className={`map-node map-${index}`}><span />{node}</div>
            ))}
          </div>
        </article>
      </div>

      <div className={`process-logs ${logsOpen ? 'open' : ''}`}>
        <button onClick={() => setLogsOpen((value) => !value)} aria-expanded={logsOpen}>
          <span>{logsOpen ? 'COLLAPSE' : 'OPEN'} AGENT LOGS</span>
          <b>{latest.length} recent steps</b>
        </button>
        {logsOpen && (
          <div className="agent-log-list">
            {latest.map((entry) => (
              <article key={entry.id}>
                <time>{entry.timestamp}</time>
                <div><b>{entry.title}</b><p>{entry.detail}</p></div>
              </article>
            ))}
          </div>
        )}
      </div>

      <div className="process-footline">
        <span>{activeProject?.name ?? 'No active project'}</span>
        <i />
        <span>{activeModel?.name ?? 'No active model'}</span>
        <i />
        <span>{snapshot.resources.activeModelTasks}/{snapshot.resources.concurrencyLimit} model lane(s)</span>
      </div>
    </section>
  );
}
