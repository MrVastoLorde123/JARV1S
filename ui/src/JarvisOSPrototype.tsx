import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot, ProjectState } from './contracts';
import './jarvis-os-prototype.css';

type Lens = 'MISSION' | 'CONTEXT' | 'RUNTIME' | 'ABILITY';
const lenses: Array<{ id: Lens; label: string; detail: string }> = [
  { id: 'MISSION', label: 'MISSION', detail: 'what matters now' },
  { id: 'CONTEXT', label: 'CONTEXT', detail: 'what informs it' },
  { id: 'RUNTIME', label: 'RUNTIME', detail: 'what constrains it' },
  { id: 'ABILITY', label: 'ABILITY', detail: 'what can act' },
];

function tone(snapshot: JarvisSnapshot) {
  if (!snapshot.online) return 'OFFLINE';
  if (snapshot.attentionRequired) return 'ATTENTION';
  if (snapshot.resources.pressure === 'HIGH') return 'GUARDED';
  if (snapshot.mode === 'Waiting') return 'WAITING';
  return 'ACTIVE';
}

function AppOS() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [lens, setLens] = useState<Lens>('MISSION');
  const [selectedProjectId, setSelectedProjectId] = useState('jarvis-interface');
  const [composer, setComposer] = useState('');
  const [commandOpen, setCommandOpen] = useState(false);
  const [event, setEvent] = useState('Ready');

  useEffect(() => demoGateway.subscribe('jarvis-os', (next) => {
    setEvent(next.detail ? `${next.title} · ${next.detail}` : next.title);
    setSnapshot(demoGateway.snapshotSync());
  }), []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); setCommandOpen((v) => !v); }
      if (e.key === 'Escape') setCommandOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const selected = snapshot.projects.find((p) => p.id === selectedProjectId) ?? snapshot.projects[0];
  const workspace = snapshot.workspaces.find((w) => w.id === selected?.workspaceId);
  const activeModel = snapshot.models.find((m) => m.state === 'ACTIVE');
  const activeLanes = snapshot.models.filter((m) => m.state !== 'OFFLINE');
  const state = tone(snapshot);
  const stateText = snapshot.attentionRequired ? 'JARVIS NEEDS YOU' : snapshot.online ? snapshot.mode.toUpperCase() : 'CORE UNAVAILABLE';

  const submit = async () => {
    const text = composer.trim();
    if (!text) return;
    setComposer('');
    const result = await demoGateway.submit({ text, sessionId: 'desktop', surface: 'CONVERSATION', projectId: selectedProjectId });
    setEvent(result.detail ? `${result.title} · ${result.detail}` : result.title);
    setSnapshot(demoGateway.snapshotSync());
    setLens('MISSION');
  };

  const projectAction = async (next: Extract<ProjectState, 'ACTIVE' | 'PAUSED'>) => {
    if (!selected) return;
    const result = await demoGateway.submit({ text: `${next === 'PAUSED' ? 'Pause' : 'Resume'} project ${selected.id}`, sessionId: 'desktop', surface: 'PROJECTS', projectId: selected.id });
    setEvent(result.title);
    setSnapshot(demoGateway.snapshotSync());
  };

  const missionIndex = Math.max(0, snapshot.projects.findIndex((p) => p.id === selected?.id));
  const operation = useMemo(() => [
    { label: 'INTENT', value: snapshot.currentFocus, detail: 'The objective entering the machine.' },
    { label: 'MISSION', value: selected?.name ?? 'No mission', detail: selected?.currentAction ?? 'Waiting for a mission object.' },
    { label: 'CONTEXT', value: workspace?.name ?? 'Unbound', detail: `${snapshot.researchTopics.length} research roots · ${snapshot.plans.length} plans.` },
    { label: 'ABILITY', value: activeModel?.name ?? 'No model', detail: `${snapshot.activeCapabilities} active capabilities · ${activeLanes.length} usable model lanes.` },
  ], [snapshot, selected, workspace, activeModel, activeLanes.length]);

  return <div className={`jarvis-os os-${state.toLowerCase()}`} data-lens={lens.toLowerCase()}>
    <header className="os-chrome">
      <button className="os-brand" onClick={() => setLens('MISSION')} aria-label="JARVIS home"><span className="os-brand-mark">J</span><span>JARVIS</span></button>
      <div className="os-location"><span>JARVIS OS</span><i /> <b>{lens}</b></div>
      <div className="os-chrome-right"><span className={`os-presence ${snapshot.online ? 'online' : 'offline'}`}><i />{snapshot.online ? 'CORE ONLINE' : 'CORE OFFLINE'}</span><button className="os-command" onClick={() => setCommandOpen(true)}>COMMAND <kbd>Ctrl K</kbd></button></div>
    </header>

    <aside className="os-rail">
      <div className="rail-label">LENSES</div>
      {lenses.map((item) => <button key={item.id} className={`lens-button ${lens === item.id ? 'active' : ''}`} onClick={() => setLens(item.id)}><span>{item.id === lens ? '●' : '○'}</span><b>{item.label}</b><small>{item.detail}</small></button>)}
      <div className="rail-spacer" />
      <div className="rail-projects"><span>MISSIONS</span>{snapshot.projects.map((project) => <button key={project.id} className={selected?.id === project.id ? 'project-dot active' : 'project-dot'} onClick={() => { setSelectedProjectId(project.id); setLens('MISSION'); }}><i /><b>{project.name}</b><small>{project.progress ?? 0}% · {project.state}</small></button>)}</div>
    </aside>

    <main className="os-main">
      <section className="os-focus-row">
        <div><span className="os-kicker">CURRENT STATE</span><h1>{stateText}</h1><p>{snapshot.currentFocus}</p></div>
        <div className="os-state-card"><span>OPERATION</span><b>{selected?.name ?? snapshot.currentFocus}</b><small>{event}</small></div>
      </section>

      <section className="os-causal">
        <div className="causal-line" />
        {operation.map((item, index) => <div key={item.label} className={`causal-node ${index <= missionIndex ? 'reached' : ''} ${index === 1 ? 'current' : ''}`}><span>{String(index + 1).padStart(2, '0')}</span><b>{item.label}</b><strong>{item.value}</strong><small>{item.detail}</small></div>)}
      </section>

      <section className="os-workbench">
        {lens === 'MISSION' && <MissionLens snapshot={snapshot} selected={selected} workspace={workspace} onPause={() => void projectAction('PAUSED')} onResume={() => void projectAction('ACTIVE')} />}
        {lens === 'CONTEXT' && <ContextLens snapshot={snapshot} selected={selected} />}
        {lens === 'RUNTIME' && <RuntimeLens snapshot={snapshot} activeModel={activeModel} />}
        {lens === 'ABILITY' && <AbilityLens snapshot={snapshot} />}
      </section>

      <section className="os-input">
        <div className="input-prefix"><span>J</span><b>DIRECT JARVIS</b></div>
        <textarea value={composer} onChange={(e) => setComposer(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void submit(); } }} placeholder="Tell JARVIS what you want to accomplish..." />
        <button onClick={() => void submit()} aria-label="Send to JARVIS">↑</button>
      </section>
    </main>

    <aside className="os-inspector">
      <div className="inspector-head"><span>OPERATOR VIEW</span><b>{state}</b></div>
      <div className="inspector-block"><span>MISSION</span><b>{selected?.name ?? 'Unbound'}</b><p>{selected?.detail ?? 'Select a mission.'}</p></div>
      <div className="inspector-block"><span>WORKSPACE</span><b>{workspace?.name ?? 'Unbound'}</b><p>{workspace?.path ?? 'No explicit workspace boundary.'}</p></div>
      <div className="inspector-block"><span>MODEL LANE</span><b>{activeModel?.name ?? 'None'}</b><p>{activeModel?.detail ?? 'No active model is currently represented.'}</p></div>
      <div className="inspector-block"><span>WHAT NEEDS YOU</span><b>{snapshot.attentionRequired ? 'DECISION REQUIRED' : 'NOTHING'}</b><p>{snapshot.attentionReason}</p></div>
      <div className="inspector-actions"><button onClick={() => setLens('CONTEXT')}>Inspect context</button><button onClick={() => setLens('RUNTIME')}>Inspect runtime</button></div>
    </aside>

    <footer className="os-status"><span><i /> {snapshot.online ? 'JARVIS CORE CONNECTED' : 'JARVIS CORE DISCONNECTED'}</span><span>{snapshot.resources.pressure} PRESSURE</span><span>{snapshot.resources.activeModelTasks}/{snapshot.resources.concurrencyLimit} MODEL TASKS</span><span>{snapshot.projects.length} MISSIONS</span></footer>

    {commandOpen && <div className="os-command-overlay" onMouseDown={() => setCommandOpen(false)}><div className="os-command-panel" onMouseDown={(e) => e.stopPropagation()}><div><span>JARVIS COMMAND</span><button onClick={() => setCommandOpen(false)}>ESC</button></div>{lenses.map((item) => <button key={item.id} onClick={() => { setLens(item.id); setCommandOpen(false); }}><b>{item.label}</b><small>{item.detail}</small><em>OPEN</em></button>)}</div></div>}
  </div>;
}

function MissionLens({ snapshot, selected, workspace, onPause, onResume }: { snapshot: JarvisSnapshot; selected: JarvisSnapshot['projects'][number] | undefined; workspace: JarvisSnapshot['workspaces'][number] | undefined; onPause: () => void; onResume: () => void }) {
  const working = selected?.state === 'ACTIVE';
  return <div className="lens-grid mission-lens"><div className="surface hero-surface"><span className="os-kicker">ACTIVE MISSION</span><h2>{selected?.name ?? 'No mission selected'}</h2><p>{selected?.detail ?? 'JARVIS is waiting for a mission object.'}</p><div className="hero-meta"><span>{selected?.progress ?? 0}%</span><span>{workspace?.name ?? 'NO WORKSPACE'}</span><span>{selected?.state ?? 'IDLE'}</span></div><div className="mission-progress"><i style={{ width: `${selected?.progress ?? 0}%` }} /></div><div className="surface-actions">{working ? <button onClick={onPause}>Pause mission</button> : <button onClick={onResume} disabled={selected?.state !== 'PAUSED'}>Resume mission</button>}<small>{snapshot.mode} · {snapshot.workRuntime.state}</small></div></div><div className="surface mission-next"><span className="os-kicker">NEXT TRANSITION</span><strong>{selected?.currentAction ?? 'Waiting for direction'}</strong><p>JARVIS preserves the operation and carries its context forward rather than forcing you to restate it.</p><div className="transition-stages"><span className="done">INTENT</span><i /><span className="done">CONTEXT</span><i /><span className="active">ACTION</span><i /><span>VERIFY</span></div></div><div className="surface mission-feed"><div className="surface-head"><span className="os-kicker">RECENT SIGNALS</span><small>{snapshot.selfActivity.length} OBSERVED</small></div>{snapshot.selfActivity.map((item) => <div className="feed-row" key={item.id}><i className={`sig sig-${item.kind.toLowerCase()}`} /><div><b>{item.title}</b><p>{item.detail}</p></div><time>{item.timestamp}</time></div>)}</div></div>;
}

function ContextLens({ snapshot, selected }: { snapshot: JarvisSnapshot; selected: JarvisSnapshot['projects'][number] | undefined }) {
  const domains = [
    ['MEMORY', `${snapshot.projects.length + snapshot.plans.length} durable roots`, 'Projects and plans provide the current operational frame.'],
    ['RESEARCH', `${snapshot.researchTopics.length} topics`, 'Evidence and questions remain attached to context.'],
    ['PLANS', `${snapshot.plans.length} plans`, 'Future work stays separate from immediate execution.'],
    ['LEARNING', `${snapshot.selfActivity.filter((item) => item.kind === 'THINKING' || item.kind === 'RESOURCE_GUARD').length} signals`, 'Learning-shaped runtime evidence is kept distinct from truth.'],
  ];
  return <div className="lens-grid context-lens"><div className="surface context-center"><span className="os-kicker">CONTEXT FIELD</span><h2>{selected?.name ?? snapshot.currentFocus}</h2><p>{selected?.currentAction ?? snapshot.currentFocus}</p><div className="context-rings"><span className="ring ring-a">MEMORY</span><span className="ring ring-b">WORK</span><span className="ring ring-c">PLAN</span><span className="ring ring-core">NOW</span></div></div><div className="surface domain-grid">{domains.map(([name, value, detail]) => <article key={name}><span>{name}</span><b>{value}</b><p>{detail}</p></article>)}</div></div>;
}

function RuntimeLens({ snapshot, activeModel }: { snapshot: JarvisSnapshot; activeModel: JarvisSnapshot['models'][number] | undefined }) {
  const resources = [['CPU', snapshot.resources.cpuLoad], ['MEM', snapshot.resources.memoryLoad], ['GPU', snapshot.resources.gpuLoad]] as const;
  return <div className="lens-grid runtime-lens"><div className="surface runtime-core"><span className="os-kicker">RUNTIME FIELD</span><div className={`runtime-orb pressure-${snapshot.resources.pressure.toLowerCase()}`}><b>{snapshot.resources.activeModelTasks}/{snapshot.resources.concurrencyLimit}</b><small>TASKS</small></div><div className="resource-stack">{resources.map(([label, value]) => <div key={label}><span>{label}</span><b>{value}%</b><i><em style={{ width: `${value}%` }} /></i></div>)}</div></div><div className="surface runtime-models"><div className="surface-head"><span className="os-kicker">MODEL FIELD</span><small>{activeModel?.name ?? 'NO ACTIVE MODEL'}</small></div>{snapshot.models.map((model) => <div className={`runtime-model state-${model.state.toLowerCase()}`} key={model.id}><i /><div><b>{model.name}</b><span>{model.role}</span></div><strong>{model.state}</strong></div>)}<p>Runtime state is observation. It shapes safe presentation and operator awareness but does not become authority by itself.</p></div></div>;
}

function AbilityLens({ snapshot }: { snapshot: JarvisSnapshot }) {
  return <div className="lens-grid ability-lens"><div className="surface ability-header"><span className="os-kicker">ABILITY FABRIC</span><h2>{snapshot.activeCapabilities} capabilities active.</h2><p>One capability fabric. Many resources. Every invocation still crosses the backend authority path.</p><div className="ability-chain"><span>DISCOVER</span><i /><span>INSPECT</span><i /><span>SCOPE</span><i /><span>INVOKE</span><i /><span>VERIFY</span></div></div><div className="surface ability-grid">{snapshot.capabilities.map((capability) => <article key={capability.id} className={`ability-${capability.state.toLowerCase()}`}><div><i /><b>{capability.name}</b><strong>{capability.state}</strong></div><p>{capability.detail}</p></article>)}</div></div>;
}

export default AppOS;
