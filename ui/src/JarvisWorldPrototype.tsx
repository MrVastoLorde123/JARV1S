import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot, ProjectState } from './contracts';
import './jarvis-world-prototype.css';

type WorldFocus = 'CORE' | 'MISSION' | 'CONTEXT' | 'RUNTIME' | 'ABILITY';

function worldState(snapshot: JarvisSnapshot) {
  if (!snapshot.online) return 'OFFLINE';
  if (snapshot.attentionRequired) return 'ATTENTION';
  if (snapshot.resources.pressure === 'HIGH') return 'GUARDED';
  if (snapshot.mode === 'Waiting') return 'WAITING';
  return 'ACTIVE';
}

function AppWorld() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [selectedId, setSelectedId] = useState('jarvis-interface');
  const [focus, setFocus] = useState<WorldFocus>('CORE');
  const [composer, setComposer] = useState('');
  const [event, setEvent] = useState('The world is listening.');
  const [inspecting, setInspecting] = useState(false);

  useEffect(() => demoGateway.subscribe('jarvis-world', (next) => {
    setEvent(next.detail ? `${next.title} · ${next.detail}` : next.title);
    setSnapshot(demoGateway.snapshotSync());
  }), []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        document.getElementById('world-input')?.focus();
      }
      if (e.key === 'Escape') {
        setFocus('CORE');
        setInspecting(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const selected = snapshot.projects.find((project) => project.id === selectedId) ?? snapshot.projects[0];
  const workspace = snapshot.workspaces.find((item) => item.id === selected?.workspaceId);
  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE');
  const state = worldState(snapshot);

  const submit = async () => {
    const text = composer.trim();
    if (!text) return;
    setComposer('');
    const result = await demoGateway.submit({ text, sessionId: 'world', surface: 'CONVERSATION', projectId: selected?.id });
    setEvent(result.detail ? `${result.title} · ${result.detail}` : result.title);
    setSnapshot(demoGateway.snapshotSync());
    setFocus('MISSION');
  };

  const setProjectState = async (next: Extract<ProjectState, 'ACTIVE' | 'PAUSED'>) => {
    if (!selected) return;
    const result = await demoGateway.submit({
      text: `${next === 'PAUSED' ? 'Pause' : 'Resume'} project ${selected.id}`,
      sessionId: 'world',
      surface: 'WORKSPACE',
      projectId: selected.id,
    });
    setEvent(result.detail ? `${result.title} · ${result.detail}` : result.title);
    setSnapshot(demoGateway.snapshotSync());
  };

  const missionNodes = useMemo(() => snapshot.projects.map((project, index) => ({
    project,
    x: [16, 13, 21][index] ?? 14,
    y: [32, 62, 77][index] ?? 52,
  })), [snapshot.projects]);

  const modelNodes = useMemo(() => snapshot.models.map((model, index) => ({
    model,
    x: [77, 88, 82][index] ?? 84,
    y: [30, 56, 75][index] ?? 50,
  })), [snapshot.models]);

  return (
    <div className={`jarvis-world world-${state.toLowerCase()} focus-${focus.toLowerCase()}`}>
      <div className="world-noise" />
      <div className="world-ambient ambient-one" />
      <div className="world-ambient ambient-two" />
      <div className="world-scanline" />

      <header className="world-topbar">
        <button className="world-wordmark" onClick={() => setFocus('CORE')} aria-label="Return to JARVIS core">
          <span className="wordmark-glyph">J</span>
          <span><b>JARVIS</b><small>WORLD</small></span>
        </button>
        <div className="world-state">
          <i />
          <span>{snapshot.mode.toUpperCase()}</span>
          <em>{snapshot.currentFocus}</em>
        </div>
        <div className="world-top-right">
          <span>{snapshot.resources.activeModelTasks}/{snapshot.resources.concurrencyLimit} MODEL TASKS</span>
          <span>{snapshot.resources.pressure} PRESSURE</span>
          <span>{snapshot.online ? 'CORE ONLINE' : 'CORE OFFLINE'}</span>
        </div>
      </header>

      <main className="world-space">
        <div className="world-field">
          <div className="field-grid" />
          <div className="world-orbit orbit-outer" />
          <div className="world-orbit orbit-inner" />
          <div className="world-orbit orbit-context" />

          <button className="world-node context-node" onClick={() => setFocus('CONTEXT')}>
            <span className="node-halo" />
            <b>CONTEXT</b>
            <small>{snapshot.projects.length + snapshot.plans.length + snapshot.researchTopics.length} roots</small>
          </button>

          {missionNodes.map(({ project, x, y }) => (
            <button
              key={project.id}
              className={`world-node mission-node ${selected?.id === project.id ? 'selected' : ''} state-${project.state.toLowerCase()}`}
              style={{ left: `${x}%`, top: `${y}%` }}
              onClick={() => { setSelectedId(project.id); setFocus('MISSION'); }}
            >
              <span className="node-line" />
              <i />
              <b>{project.name}</b>
              <small>{project.progress ?? 0}% · {project.state}</small>
            </button>
          ))}

          {modelNodes.map(({ model, x, y }) => (
            <button
              key={model.id}
              className={`world-node ability-node model-${model.state.toLowerCase()}`}
              style={{ left: `${x}%`, top: `${y}%` }}
              onClick={() => setFocus('ABILITY')}
            >
              <span className="node-line" />
              <i />
              <b>{model.name}</b>
              <small>{model.role}</small>
            </button>
          ))}

          <button className="world-node runtime-node" onClick={() => setFocus('RUNTIME')}>
            <span className="runtime-pulse" />
            <b>RUNTIME</b>
            <small>{snapshot.resources.cpuLoad}% CPU · {snapshot.resources.memoryLoad}% MEM</small>
          </button>

          <div className="world-core-shell">
            <button className="world-core" onClick={() => { setFocus('CORE'); setInspecting(false); }} aria-label="JARVIS core">
              <span className="core-ring ring-one" />
              <span className="core-ring ring-two" />
              <span className="core-ring ring-three" />
              <span className="core-mark">J</span>
              <small>{state}</small>
            </button>
            <div className="core-caption">
              <span>{focus === 'CORE' ? 'JARVIS' : focus}</span>
              <b>{selected?.name ?? 'No mission'}</b>
              <small>{event}</small>
            </div>
          </div>

          {snapshot.attentionRequired && (
            <button className="attention-node" onClick={() => setInspecting(true)}>
              <span>ATTENTION</span>
              <b>{snapshot.attentionReason}</b>
              <small>Open the decision surface</small>
            </button>
          )}

          <div className="world-traces" aria-hidden="true">
            <span className="trace trace-a" />
            <span className="trace trace-b" />
            <span className="trace trace-c" />
            <span className="trace trace-d" />
          </div>
        </div>

        <section className={`world-detail ${focus === 'CORE' ? 'collapsed' : ''}`}>
          {focus === 'MISSION' && <MissionDetail selected={selected} workspace={workspace} onPause={() => void setProjectState('PAUSED')} onResume={() => void setProjectState('ACTIVE')} />}
          {focus === 'CONTEXT' && <ContextDetail snapshot={snapshot} />}
          {focus === 'RUNTIME' && <RuntimeDetail snapshot={snapshot} />}
          {focus === 'ABILITY' && <AbilityDetail snapshot={snapshot} activeModel={activeModel} />}
        </section>

        <section className="world-input-wrap">
          <div className="world-input-label"><span className="input-glyph">J</span><span>Speak into the world</span><kbd>Ctrl K</kbd></div>
          <textarea
            id="world-input"
            value={composer}
            onChange={(e) => setComposer(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void submit(); } }}
            placeholder="Tell JARVIS what should happen next..."
          />
          <button onClick={() => void submit()} disabled={!composer.trim()} aria-label="Send command">↗</button>
        </section>
      </main>

      <footer className="world-footer">
        <span><i className={snapshot.online ? 'online' : 'offline'} />{snapshot.online ? 'JARVIS is present' : 'JARVIS is disconnected'}</span>
        <span>{snapshot.activeWork} active work</span>
        <span>{snapshot.monitoredSources} monitored sources</span>
        <span>{snapshot.capabilities.filter((item) => item.state !== 'OFFLINE').length} live abilities</span>
        <button onClick={() => setInspecting((value) => !value)}>{inspecting ? 'Close inspector' : 'Open inspector'} · {snapshot.attentionRequired ? '1 decision' : 'quiet'}</button>
      </footer>

      {inspecting && <WorldInspector snapshot={snapshot} selected={selected} onClose={() => setInspecting(false)} />}
    </div>
  );
}

function MissionDetail({ selected, workspace, onPause, onResume }: { selected: JarvisSnapshot['projects'][number] | undefined; workspace: JarvisSnapshot['workspaces'][number] | undefined; onPause: () => void; onResume: () => void }) {
  const isActive = selected?.state === 'ACTIVE';
  return <div className="detail-card mission-detail-card"><div><span>MISSION IN VIEW</span><h2>{selected?.name ?? 'No mission'}</h2><p>{selected?.detail ?? 'Nothing selected.'}</p></div><div className="detail-stats"><b>{selected?.progress ?? 0}%</b><span>{selected?.currentAction ?? 'No current action'}</span><span>{workspace?.name ?? 'No workspace'}</span></div><div className="detail-actions">{isActive ? <button onClick={onPause}>Pause</button> : <button onClick={onResume} disabled={selected?.state !== 'PAUSED'}>Resume</button>}<small>{selected?.state ?? 'IDLE'}</small></div></div>;
}

function ContextDetail({ snapshot }: { snapshot: JarvisSnapshot }) {
  return <div className="detail-card context-detail-card"><div><span>CONTEXT FIELD</span><h2>Everything JARVIS currently carries.</h2><p>Context is spatial here: it sits around the work instead of living behind another screen.</p></div><div className="detail-columns"><article><b>{snapshot.projects.length}</b><span>missions</span></article><article><b>{snapshot.researchTopics.length}</b><span>research roots</span></article><article><b>{snapshot.plans.length}</b><span>plans</span></article><article><b>{snapshot.selfActivity.length}</b><span>self signals</span></article></div></div>;
}

function RuntimeDetail({ snapshot }: { snapshot: JarvisSnapshot }) {
  const values = [['CPU', snapshot.resources.cpuLoad], ['MEM', snapshot.resources.memoryLoad], ['GPU', snapshot.resources.gpuLoad]] as const;
  return <div className="detail-card runtime-detail-card"><div><span>RUNTIME FIELD</span><h2>{snapshot.resources.pressure} pressure</h2><p>{snapshot.resources.activeModelTasks} of {snapshot.resources.concurrencyLimit} model lanes are occupied. Runtime informs the environment; it does not become authority.</p></div><div className="runtime-meters">{values.map(([label, value]) => <div key={label}><span>{label}</span><b>{value}%</b><i><em style={{ width: `${value}%` }} /></i></div>)}</div></div>;
}

function AbilityDetail({ snapshot, activeModel }: { snapshot: JarvisSnapshot; activeModel: JarvisSnapshot['models'][number] | undefined }) {
  return <div className="detail-card ability-detail-card"><div><span>ABILITY FIELD</span><h2>{activeModel?.name ?? 'No active model'}</h2><p>{activeModel?.detail ?? 'The model fabric is waiting for a usable lane.'}</p></div><div className="ability-list">{snapshot.capabilities.map((item) => <span key={item.id}><i />{item.name}<small>{item.state}</small></span>)}</div></div>;
}

function WorldInspector({ snapshot, selected, onClose }: { snapshot: JarvisSnapshot; selected: JarvisSnapshot['projects'][number] | undefined; onClose: () => void }) {
  return <aside className="world-inspector"><div className="inspector-top"><span>LOCAL INSPECTOR</span><button onClick={onClose}>×</button></div><section><span>NOW</span><b>{snapshot.mode}</b><p>{snapshot.currentFocus}</p></section><section><span>MISSION</span><b>{selected?.name ?? 'None'}</b><p>{selected?.currentAction ?? 'No active action'}</p></section><section><span>MODEL</span><b>{snapshot.models.find((item) => item.state === 'ACTIVE')?.name ?? 'None'}</b><p>{snapshot.resources.strategy} execution · {snapshot.resources.pressure} pressure</p></section><section><span>SELF SIGNAL</span><b>{snapshot.selfActivity[0]?.title ?? 'Quiet'}</b><p>{snapshot.selfActivity[0]?.detail ?? 'No signal.'}</p></section><div className="inspector-rule" /><small>This panel is intentionally transient. The world remains the primary interface.</small></aside>;
}

export default AppWorld;
