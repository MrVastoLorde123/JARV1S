import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { ChatSurface, JarvisMode, JarvisSnapshot, WorkControlState } from './contracts';

const spaces = ['HOME', 'CHAT', 'WORK', 'MIND', 'CAPABILITIES', 'SELF'] as const;
type Space = typeof spaces[number];

const modeLabels: Record<JarvisMode, string> = {
  Thinking: 'COGNITIVE LOOP', Learning: 'LEARNING', Working: 'WORKING', Monitoring: 'MONITORING', Waiting: 'STANDING BY', 'Needs You': 'ATTENTION REQUIRED',
};

function App() {
  const [space, setSpace] = useState<Space>('HOME');
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [composer, setComposer] = useState('');
  const [chat, setChat] = useState<string[]>([]);
  const [lastEvent, setLastEvent] = useState('System initialized');
  const [chatSurface, setChatSurface] = useState<ChatSurface>('CONVERSATION');
  const [workControl, setWorkControl] = useState<WorkControlState>('RUNNING');

  useEffect(() => demoGateway.subscribe('desktop', (event) => {
    setLastEvent(event.detail ? `${event.title} — ${event.detail}` : event.title);
    setSnapshot(demoGateway.snapshotSync());
  }), []);

  const current = useMemo(() => ({ ...snapshot, modeLabel: modeLabels[snapshot.mode] }), [snapshot]);

  const submit = async () => {
    const value = composer.trim();
    if (!value) return;
    setChat((items) => [...items, value]);
    setComposer('');
    setSpace('CHAT');
    const event = await demoGateway.submit({ text: value, sessionId: 'desktop' });
    setLastEvent(event.title);
    setSnapshot(demoGateway.snapshotSync());
  };

  const toggleWorkControl = async () => {
    const next = workControl === 'RUNNING' ? 'PAUSED' : 'RUNNING';
    setWorkControl(next);
    const event = await demoGateway.submit({ text: next === 'PAUSED' ? 'Pause current work execution' : 'Resume current work execution', sessionId: 'desktop' });
    setLastEvent(event.title);
    setSnapshot(demoGateway.snapshotSync());
  };

  return (
    <div className={`shell mode-${snapshot.mode.toLowerCase().replace(/\s+/g, '-')}`}>
      <div className="ambient ambient-a" /><div className="ambient ambient-b" />
      <div className="ambient-core" aria-hidden="true"><span /></div>
      <header className="topbar">
        <button className="brand" onClick={() => setSpace('HOME')} aria-label="Return to JARVIS Home"><span className="brand-mark">J</span><span>JARVIS</span></button>
        <div className="presence"><span className="pulse" />{snapshot.online ? 'ONLINE' : 'OFFLINE'}<span className="presence-detail">{current.modeLabel}</span></div>
        <div className="top-meta">COGNITIVE ACTIVITY <strong>{current.cognitiveActivity}</strong><span className="top-separator">·</span>UPTIME <strong>{snapshot.uptime}</strong></div>
      </header>
      <main className="layout">
        <section className="hero">
          <div className="hero-eyebrow">JARVIS SYSTEM STATE</div><div className="hero-title">{snapshot.mode}</div><div className="hero-focus">{snapshot.currentFocus}</div>
          <div className="hero-metrics"><Metric label="CAPABILITIES" value={snapshot.activeCapabilities} /><Metric label="SOURCES" value={snapshot.monitoredSources} /><Metric label="ACTIVE WORK" value={snapshot.activeWork} /><Metric label="ATTENTION" value={snapshot.attentionRequired ? 'YES' : 'CLEAR'} /></div>
          <div className="live-strip"><span className="live-dot" /> LIVE · {lastEvent}</div>
        </section>
        <nav className="spaces" aria-label="JARVIS spaces">{spaces.map((item) => <button key={item} className={item === space ? 'space active' : 'space'} onClick={() => setSpace(item)}>{item}</button>)}</nav>
        {space === 'HOME' && <Home snapshot={snapshot} onNavigate={setSpace} />}
        {space === 'CHAT' && <Chat surface={chatSurface} setSurface={setChatSurface} chat={chat} composer={composer} setComposer={setComposer} submit={submit} snapshot={snapshot} />}
        {space === 'WORK' && <Work snapshot={snapshot} control={workControl} toggleControl={toggleWorkControl} />}
        {space === 'MIND' && <Mind snapshot={snapshot} />}
        {space === 'CAPABILITIES' && <Capabilities snapshot={snapshot} />}
        {space === 'SELF' && <Self snapshot={snapshot} />}
      </main>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) { return <span>{label} <b>{value}</b></span>; }

function Home({ snapshot, onNavigate }: { snapshot: JarvisSnapshot; onNavigate: (space: Space) => void }) {
  return <section className="home-grid">
    <div className="panel cockpit"><div className="panel-kicker">LIVE COCKPIT</div><div className="cockpit-body"><div><span className="signal-label">CURRENT FOCUS</span><strong>{snapshot.currentFocus}</strong><p>{snapshot.mode === 'Needs You' ? 'JARVIS is waiting for your decision.' : 'System is observing, reasoning, and maintaining current context.'}</p></div><div className="signal-ring"><span>{snapshot.cognitiveActivity}</span><small>COGNITION</small></div></div><div className="cockpit-footer"><span>Last state change</span><b>{snapshot.lastStateChange}</b></div></div>
    <div className={`panel attention ${snapshot.attentionRequired ? 'attention-hot' : ''}`}><div className="panel-kicker">ATTENTION</div><div className="attention-number">{snapshot.attentionRequired ? 'YES' : 'CLEAR'}</div><div className="attention-copy">{snapshot.attentionReason}</div><button className="text-action" onClick={() => onNavigate('WORK')}>Review work →</button></div>
    <div className="panel intelligence wide"><div className="panel-heading"><span>RECENT INTELLIGENCE</span><small>LIVE STREAM</small></div><div className="activity-list">{snapshot.activity.map((item) => <div className="activity-item" key={item.id}><span className="activity-dot" /><div><b>{item.title}</b><p>{item.detail}</p></div><time>{item.timestamp}</time></div>)}</div></div>
    <div className="panel work-overview"><div className="panel-heading"><span>WORK</span><small>{snapshot.workRuntime.state}</small></div>{snapshot.projects.map((project) => <div className="project" key={project.id}><div><b>{project.name}</b><span>{project.state}</span></div>{typeof project.progress === 'number' && <div className="bar"><span style={{ width: `${project.progress}%` }} /></div>}</div>)}<button className="panel-action" onClick={() => onNavigate('WORK')}>Open work control →</button></div>
    <div className="panel capability-overview"><div className="panel-heading"><span>CAPABILITY FABRIC</span><small>LIVE</small></div>{snapshot.capabilities.slice(0, 5).map((cap) => <div className="cap-row" key={cap.id}><span className={`state-dot ${cap.state.toLowerCase()}`} /><b>{cap.name}</b><span>{cap.state}</span></div>)}<button className="panel-action" onClick={() => onNavigate('CAPABILITIES')}>Open capabilities →</button></div>
  </section>;
}

function Chat({ surface, setSurface, chat, composer, setComposer, submit, snapshot }: { surface: ChatSurface; setSurface: (surface: ChatSurface) => void; chat: string[]; composer: string; setComposer: (value: string) => void; submit: () => void; snapshot: JarvisSnapshot }) {
  const definitions: Record<ChatSurface, { label: string; kicker: string; description: string; placeholder: string }> = {
    CONVERSATION: { label: 'Conversation', kicker: 'GENERAL INTELLIGENCE', description: 'A free conversational surface. JARVIS can reference current state, memory, work and context.', placeholder: 'Talk to JARVIS...' },
    WORKSPACE: { label: 'Workspace', kicker: 'LITERAL WORKSPACE', description: 'Select a folder, inspect its state, then generate, edit, research, or code directly against that workspace.', placeholder: 'Tell JARVIS what to build or change in this workspace...' },
    RESEARCH: { label: 'Research', kicker: 'THINKING ENGINE', description: 'Gather topics, sources and evidence, then reason over them before conclusions become plans or actions.', placeholder: 'Research a topic, gather evidence, or ask JARVIS to think on collected material...' },
    PLANNING: { label: 'Planning', kicker: 'STRATEGY SPACE', description: 'Turn goals into structured plans with dependencies, checkpoints, boundaries and execution readiness.', placeholder: 'Describe the outcome you want JARVIS to plan...' },
  };
  const active = definitions[surface];
  return <section className="chat-shell">
    <aside className="chat-sidebar panel"><div className="panel-kicker">CHAT MAP</div><button className="chat-new">+ New {active.label.toLowerCase()}</button>
      {(Object.keys(definitions) as ChatSurface[]).map((item) => <button key={item} className={item === surface ? 'chat-mode active' : 'chat-mode'} onClick={() => setSurface(item)}><span>{definitions[item].label}</span><small>{item === 'WORKSPACE' ? 'FOLDER' : item === 'RESEARCH' ? 'THINK' : item === 'PLANNING' ? 'PLAN' : 'TALK'}</small></button>)}
      {surface === 'WORKSPACE' && <div className="chat-toolbox"><span className="panel-kicker">ACTIVE WORKSPACE</span>{snapshot.workspaces.map((workspace) => <button className={`workspace-item ${workspace.status === 'SELECTED' ? 'selected' : ''}`} key={workspace.id}><b>{workspace.name}</b><small>{workspace.path}</small></button>)}<button className="soft-action">+ Create workspace</button></div>}
      {surface === 'RESEARCH' && <div className="chat-toolbox"><span className="panel-kicker">TOPICS</span>{snapshot.researchTopics.map((topic) => <button className={`research-topic ${topic.state === 'ACTIVE' ? 'selected' : ''}`} key={topic.id}><b>{topic.title}</b><small>{topic.state}</small></button>)}<button className="soft-action">+ Gather new topic</button></div>}
      {surface === 'PLANNING' && <div className="chat-toolbox"><span className="panel-kicker">PLANS</span>{snapshot.plans.map((plan) => <button className="plan-item" key={plan.id}><b>{plan.title}</b><small>{plan.state}</small></button>)}<button className="soft-action">+ New plan</button></div>}
      {surface === 'CONVERSATION' && <div className="chat-context"><span className="panel-kicker">ACTIVE CONTEXT</span><b>{snapshot.currentFocus}</b><p>HOME state, work state, capabilities and relevant memory can be referenced here.</p></div>}
    </aside>
    <section className="panel chat-main"><div className="chat-header"><div><span className="panel-kicker">{active.kicker}</span><h1>{active.label}</h1><p>{active.description}</p></div><span className="chat-status"><i /> context-aware</span></div>
      {surface === 'WORKSPACE' && <WorkspaceSurface snapshot={snapshot} />}{surface === 'RESEARCH' && <ResearchSurface snapshot={snapshot} />}{surface === 'PLANNING' && <PlanningSurface snapshot={snapshot} />}{surface === 'CONVERSATION' && <ConversationSurface chat={chat} />}
      <div className="chat-composer"><textarea value={composer} onChange={(e) => setComposer(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } }} placeholder={active.placeholder} /><button onClick={submit}>↑</button></div>
    </section>
  </section>;
}

function ConversationSurface({ chat }: { chat: string[] }) { return <div className="chat-history">{chat.length === 0 ? <div className="chat-empty"><span className="empty-orb" /><h2>Talk to JARVIS.</h2><p>This is the general conversational layer. Other Chat surfaces deliberately become specialized when the task needs a different operating mode.</p></div> : chat.map((message, index) => <div className="chat-message" key={`${message}-${index}`}><span>YOU</span><p>{message}</p></div>)}</div>; }

function WorkspaceSurface({ snapshot }: { snapshot: JarvisSnapshot }) { const selected = snapshot.workspaces.find((item) => item.status === 'SELECTED'); return <div className="special-surface"><div className="workspace-banner"><div><span className="surface-label">WORKSPACE ROOT</span><h2>{selected?.name ?? 'No workspace selected'}</h2><p>{selected?.path ?? 'Select or create a folder to begin.'}</p></div><span className="surface-state">READY</span></div><div className="workspace-grid"><div className="surface-card"><span>INSPECT</span><b>See current files and structure</b><p>JARVIS should understand where the workspace is before making changes.</p></div><div className="surface-card"><span>GENERATE</span><b>Create inside the workspace</b><p>Code, documents, assets and project scaffolding belong here.</p></div><div className="surface-card"><span>EDIT</span><b>Modify existing work</b><p>Changes remain tied to the selected workspace and its context.</p></div><div className="surface-card"><span>VERIFY</span><b>Check what changed</b><p>Diffs, tests and resulting state become visible before continuation.</p></div></div></div>; }

function ResearchSurface({ snapshot }: { snapshot: JarvisSnapshot }) { const active = snapshot.researchTopics.filter((item) => item.state !== 'QUEUED'); return <div className="special-surface"><div className="research-command"><div><span className="surface-label">RESEARCH QUEUE</span><h2>Think before concluding.</h2><p>Topics can be gathered, revisited, challenged and explicitly thought on.</p></div><button className="primary-action">+ Add topic</button></div><div className="research-board">{active.map((topic) => <article className="research-card" key={topic.id}><div className="research-card-top"><span>{topic.state}</span><button>THINK →</button></div><h3>{topic.title}</h3><p>{topic.detail}</p><div className="research-footer"><span>Sources ready</span><b>0</b></div></article>)}</div><div className="thinking-lane"><span>ENGINEER / THINKING</span><b>Research should become a place where JARVIS can reason over what it gathered, not merely display search results.</b></div></div>; }

function PlanningSurface({ snapshot }: { snapshot: JarvisSnapshot }) { return <div className="special-surface"><div className="planning-command"><span className="surface-label">PLANNING WORKBENCH</span><h2>Outcome → structure → execution.</h2><p>Plans are deliberate artifacts with steps, dependencies, checkpoints and a clear readiness state.</p></div><div className="plan-board">{snapshot.plans.map((plan) => <article className="plan-card" key={plan.id}><div className="plan-card-top"><span>{plan.state}</span>{plan.currentStep ? <b>STEP {plan.currentStep}/{plan.steps.length}</b> : <b>{plan.steps.length} STEPS</b>}</div><h3>{plan.title}</h3>{plan.steps.map((step, index) => <div className={`plan-step ${plan.currentStep === index + 1 ? 'current' : ''}`} key={step}><span>{index + 1}</span>{step}</div>)}</article>)}</div></div>; }

function Work({ snapshot, control, toggleControl }: { snapshot: JarvisSnapshot; control: WorkControlState; toggleControl: () => void }) { return <section className="space-panel panel"><div className="work-control-head"><div><div className="panel-kicker">WORK CONTROL</div><h1>Work</h1><p className="space-subtitle">See where JARVIS is, inspect progress, then pause or resume the working state before adding feedback, commands or boundaries.</p></div><button className={`control-toggle ${control === 'PAUSED' ? 'paused' : ''}`} onClick={toggleControl}><span />{control === 'PAUSED' ? 'RESUME' : 'PAUSE'}</button></div><div className={`work-runtime ${control === 'PAUSED' ? 'runtime-paused' : ''}`}><div><span className="surface-label">RUNTIME</span><strong>{control}</strong><p>{control === 'PAUSED' ? 'Execution is visually held. Add guidance before resuming.' : 'JARVIS is allowed to continue the current work state.'}</p></div><div className="runtime-command"><span>LAST CONTROL</span><b>{snapshot.workRuntime.lastCommand}</b></div></div><div className="work-grid">{snapshot.projects.map((project) => <div className="work-card" key={project.id}><div className="work-card-top"><span>{project.state}</span>{typeof project.progress === 'number' && <b>{project.progress}%</b>}</div><h3>{project.name}</h3><p>{project.state === 'WAITING' ? 'Waiting for a condition or external input.' : 'JARVIS is maintaining context and progress.'}</p>{typeof project.progress === 'number' && <div className="bar"><span style={{ width: `${project.progress}%` }} /></div>}</div>)}</div></section>; }

function Mind({ snapshot }: { snapshot: JarvisSnapshot }) { const [view, setView] = useState<'FOLDERS' | 'RELATIONSHIPS'>('FOLDERS'); const folders = ['Personal','Skills','Preferences','Projects','Goals','Facts','Workflows','Relationships','Experiences']; return <section className="space-panel panel"><div className="panel-kicker">SECOND BRAIN</div><div className="space-heading-row"><div><h1>Mind</h1><p className="space-subtitle">Memory and knowledge as a navigable system.</p></div><div className="segmented"><button className={view === 'FOLDERS' ? 'active' : ''} onClick={() => setView('FOLDERS')}>Folders</button><button className={view === 'RELATIONSHIPS' ? 'active' : ''} onClick={() => setView('RELATIONSHIPS')}>Relationships</button></div></div>{view === 'FOLDERS' ? <div className="folder-grid">{folders.map((folder) => <div className="folder" key={folder}><span>◈</span><b>{folder}</b><small>evidence-aware</small></div>)}</div> : <div className="relationship-map"><span className="node center">JARVIS</span><span className="node n1">PROJECTS</span><span className="node n2">SKILLS</span><span className="node n3">GOALS</span><span className="node n4">EXPERIENCES</span><span className="node n5">RELATIONSHIPS</span><div className="connection c1" /><div className="connection c2" /><div className="connection c3" /><div className="connection c4" /><div className="connection c5" /></div>}<div className="mind-foot"><span>Evidence model: ready for live memory</span><b>{snapshot.projects.length} project roots</b></div></section>; }

function Capabilities({ snapshot }: { snapshot: JarvisSnapshot }) { return <section className="space-panel panel"><div className="panel-kicker">CAPABILITY FABRIC</div><h1>Capabilities</h1><p className="space-subtitle">The third hand: tools, models and integrations are visible here without gaining authority.</p><div className="capability-grid">{snapshot.capabilities.map((cap) => <div className="capability-card" key={cap.id}><div><span className={`state-dot ${cap.state.toLowerCase()}`} /><b>{cap.name}</b><span>{cap.state}</span></div><p>{cap.detail}</p></div>)}</div><div className="expansion-rail"><span>EXTENSIBILITY</span><b>Models · Plugins · Integrations · Workers · Interfaces</b><p>Each capability can grow independently while remaining inside the JARVIS authority boundary.</p></div></section>; }

function Self({ snapshot }: { snapshot: JarvisSnapshot }) { return <section className="space-panel panel"><div className="panel-kicker">SELF OBSERVATION</div><h1>Self</h1><p className="space-subtitle">JARVIS should be able to explain itself until you understand it.</p><div className="self-grid">{[['Architecture','Core authority remains backend-owned.'],['Runtime','Live state is available through the gateway boundary.'],['Memory','Evidence-aware knowledge is visible to the user.'],['Learning','Learning signals remain separate from truth and authority.'],['Security','Hardening becomes a dedicated final phase after capability expansion.'],['Performance',`Current focus: ${snapshot.currentFocus}`],['Updates','Changes should be explainable and verified.'],['Experiments','Experimental capabilities remain visibly distinct.']].map(([title, detail]) => <div className="self-card" key={title}><span>{title}</span><p>{detail}</p></div>)}</div><div className="self-expansion"><span>SELF SURFACE</span><b>Explain · Inspect · Learn · Compare · Configure</b><p>This is intentionally expansive. JARVIS should be able to expose more of its own architecture as the system grows.</p></div></section>; }

export default App;
