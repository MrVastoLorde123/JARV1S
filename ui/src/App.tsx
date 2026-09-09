import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { ChatSurface, JarvisMode, JarvisSnapshot, ProjectState } from './contracts';
import './functional.css';

type Space = 'HOME' | 'CHAT' | 'WORK' | 'CONTROL' | 'MIND' | 'CAPABILITIES' | 'SELF';
const spaces: Space[] = ['HOME', 'CHAT', 'WORK', 'CONTROL', 'MIND', 'CAPABILITIES', 'SELF'];
const spaceLabels: Record<Space, string> = { HOME: 'HOME', CHAT: 'CHAT', WORK: 'WORK', CONTROL: 'CONTROL', MIND: 'MIND', CAPABILITIES: 'CAPABILITIES', SELF: 'SELF' };
const modeLabels: Record<JarvisMode, string> = { Thinking: 'COGNITIVE LOOP', Learning: 'LEARNING', Working: 'WORKING', Monitoring: 'MONITORING', Waiting: 'STANDING BY', 'Needs You': 'ATTENTION REQUIRED' };
const chatLabels: Record<ChatSurface, string> = { CONVERSATION: 'Conversation', WORKSPACE: 'Workspace', RESEARCH: 'Research', PLANNING: 'Planning' };
const iconPaths: Record<string, string> = {
  HOME: 'M3 11 12 4l9 7M5 10v10h14V10M9 20v-6h6v6',
  CHAT: 'M4 5h16v11H8l-4 4V5',
  WORK: 'M4 6h16v13H4zM4 10h16M8 6V4h8v2',
  CONTROL: 'M4 7h16M4 12h10M4 17h16M17 9l3 3-3 3',
  MIND: 'M12 4v16M4 12h16M7 7l10 10M17 7 7 17',
  CAPABILITIES: 'M12 3l2.1 5.2L20 10l-5.9 1.8L12 17l-2.1-5.2L4 10l5.9-1.8L12 3z',
  SELF: 'M12 4a8 8 0 1 0 8 8 8 8 0 0 0-8-8zm0 3v5l3 2',
  MENU: 'M4 7h16M4 12h16M4 17h16',
};

function Icon({ name }: { name: string }) {
  return <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={iconPaths[name] ?? iconPaths.MENU} /></svg>;
}

function App() {
  const [space, setSpace] = useState<Space>('HOME');
  const [collapsed, setCollapsed] = useState(false);
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [composer, setComposer] = useState('');
  const [chatSurface, setChatSurface] = useState<ChatSurface>('CONVERSATION');
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState('jarvis');
  const [selectedProjectId, setSelectedProjectId] = useState('jarvis-interface');
  const [chatHistory, setChatHistory] = useState<Record<ChatSurface, string[]>>({ CONVERSATION: [], WORKSPACE: [], RESEARCH: [], PLANNING: [] });
  const [lastEvent, setLastEvent] = useState('Ready');
  const [commandOpen, setCommandOpen] = useState(false);

  useEffect(() => demoGateway.subscribe('desktop', (event) => {
    setLastEvent(event.detail ? `${event.title} · ${event.detail}` : event.title);
    setSnapshot(demoGateway.snapshotSync());
  }), []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); setCommandOpen((value) => !value); }
      if (event.key === 'Escape') setCommandOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const current = useMemo(() => ({ ...snapshot, modeLabel: modeLabels[snapshot.mode] }), [snapshot]);

  const navigate = (next: Space) => { setSpace(next); setCommandOpen(false); };

  const submit = async () => {
    const value = composer.trim();
    if (!value) return;
    setChatHistory((history) => ({ ...history, [chatSurface]: [...history[chatSurface], value] }));
    setComposer('');
    setSpace('CHAT');
    const event = await demoGateway.submit({ text: value, sessionId: 'desktop', surface: chatSurface });
    setLastEvent(event.title);
    setSnapshot(demoGateway.snapshotSync());
  };

  const controlProject = async (projectId: string, next: Extract<ProjectState, 'ACTIVE' | 'PAUSED'>) => {
    const event = await demoGateway.submit({ text: `${next === 'PAUSED' ? 'Pause' : 'Resume'} project ${projectId}`, sessionId: 'desktop', surface: 'PROJECTS', projectId });
    setLastEvent(event.title);
    setSnapshot(demoGateway.snapshotSync());
  };

  const selectWorkspaceDirectory = async () => {
    const picker = (window as Window & { showDirectoryPicker?: () => Promise<{ name: string }> }).showDirectoryPicker;
    if (!picker) return;
    try {
      const directory = await picker();
      const event = await demoGateway.submit({ text: `Select workspace directory ${directory.name}`, sessionId: 'desktop', surface: 'WORKSPACE' });
      const next = demoGateway.snapshotSync();
      const selected = next.workspaces.find((workspace) => workspace.name === directory.name);
      if (selected) setSelectedWorkspaceId(selected.id);
      setLastEvent(event.title);
      setSnapshot(next);
    } catch {
      setLastEvent('Workspace picker closed');
    }
  };

  const activeWorkspace = snapshot.workspaces.find((workspace) => workspace.id === selectedWorkspaceId) ?? snapshot.workspaces[0];
  const activeProject = snapshot.projects.find((project) => project.id === selectedProjectId) ?? snapshot.projects[0];
  const attentionCount = snapshot.attentionRequired ? 1 : 0;

  return <div className={`shell mode-${snapshot.mode.toLowerCase().replace(/\s+/g, '-')} ${collapsed ? 'nav-collapsed' : ''}`}>
    <div className="ambient ambient-a" /><div className="ambient ambient-b" /><div className="ambient-core" aria-hidden="true"><span /></div>
    <aside className="sidebar" aria-label="JARVIS navigation">
      <div className="sidebar-brand">
        <button className="brand" onClick={() => navigate('HOME')} aria-label="JARVIS Home"><span className="brand-mark">J</span><span className="brand-word">JARVIS</span></button>
        <button className="sidebar-toggle" onClick={() => setCollapsed((value) => !value)} aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}><Icon name="MENU" /></button>
      </div>
      <div className="sidebar-status"><span className="pulse" /> <span className="sidebar-status-text">{snapshot.online ? 'ONLINE' : 'OFFLINE'}</span><small>{current.modeLabel}</small></div>
      <div className="sidebar-group"><span className="sidebar-group-label">CORE</span>{spaces.slice(0, 4).map((item) => <NavButton key={item} item={item} active={space === item} collapsed={collapsed} onClick={() => navigate(item)} />)}</div>
      <div className="sidebar-group"><span className="sidebar-group-label">SYSTEM</span>{spaces.slice(4).map((item) => <NavButton key={item} item={item} active={space === item} collapsed={collapsed} onClick={() => navigate(item)} />)}</div>
      <div className="sidebar-spacer" />
      <div className="sidebar-foot"><span className="sidebar-resource-dot" /><div><b>{snapshot.resources.strategy === 'SEQUENTIAL' ? 'RESOURCE GUARD' : 'LIMITED CONCURRENCY'}</b><small>CPU {snapshot.resources.cpuLoad}% · MEM {snapshot.resources.memoryLoad}%</small></div></div>
    </aside>

    <header className="topbar">
      <div className="topbar-left"><span className="top-context">{spaceLabels[space]}</span><span className="top-divider" /><span className="top-focus">{snapshot.currentFocus}</span></div>
      <div className="topbar-right"><button className="command-trigger" onClick={() => setCommandOpen(true)}><span>COMMAND</span><kbd>Ctrl K</kbd></button><span className={`pressure pressure-${snapshot.resources.pressure.toLowerCase()}`}>{snapshot.resources.pressure}</span><span className="top-meta">{attentionCount ? `${attentionCount} ATTENTION · ` : ''}{snapshot.models.filter((model) => model.state === 'ACTIVE').length} MODELS · {snapshot.projects.length} WORK</span></div>
    </header>

    <main className="layout">
      <section className="hero">
        <div className="hero-eyebrow">JARVIS OPERATING ENVIRONMENT</div>
        <div className="hero-title">{snapshot.mode}</div>
        <div className="hero-focus">{snapshot.currentFocus}</div>
        <div className="hero-metrics"><Metric label="CAPABILITIES" value={snapshot.activeCapabilities} /><Metric label="SOURCES" value={snapshot.monitoredSources} /><Metric label="WORK" value={snapshot.projects.length} /><Metric label="ATTENTION" value={snapshot.attentionRequired ? 'YES' : 'CLEAR'} /></div>
        <div className="state-pulse"><span className="state-pulse-core" /><div><strong>{snapshot.mode}</strong><small>{lastEvent}</small></div><span className="state-pulse-time">{snapshot.uptime}</span></div>
      </section>

      {space === 'HOME' && <Home snapshot={snapshot} navigate={navigate} />}
      {space === 'CHAT' && <Chat surface={chatSurface} setSurface={setChatSurface} history={chatHistory[chatSurface]} composer={composer} setComposer={setComposer} submit={submit} snapshot={snapshot} selectedWorkspaceId={selectedWorkspaceId} onSelectWorkspace={setSelectedWorkspaceId} onSelectDirectory={selectWorkspaceDirectory} selectedProjectId={selectedProjectId} setSelectedProjectId={setSelectedProjectId} navigate={navigate} />}
      {space === 'WORK' && <Projects snapshot={snapshot} selectedProjectId={selectedProjectId} setSelectedProjectId={setSelectedProjectId} controlProject={controlProject} onNavigate={navigate} />}
      {space === 'CONTROL' && <MissionControl snapshot={snapshot} selectedProjectId={selectedProjectId} setSelectedProjectId={setSelectedProjectId} onOpenWork={() => navigate('WORK')} onOpenChat={() => navigate('CHAT')} />}
      {space === 'MIND' && <Mind snapshot={snapshot} onOpenControl={() => navigate('CONTROL')} />}
      {space === 'CAPABILITIES' && <Capabilities snapshot={snapshot} />}
      {space === 'SELF' && <Self snapshot={snapshot} onOpenControl={() => navigate('CONTROL')} />}
    </main>

    {commandOpen && <CommandPalette close={() => setCommandOpen(false)} navigate={navigate} snapshot={snapshot} />}
    <div className="desktop-statusbar"><span><i className="status-led" /> JARVIS CORE {snapshot.online ? 'CONNECTED' : 'DISCONNECTED'}</span><span>SESSION · DESKTOP</span><span>UPTIME · {snapshot.uptime}</span><span>PRESS Ctrl K FOR COMMAND</span></div>
  </div>;
}

function NavButton({ item, active, collapsed, onClick }: { item: Space; active: boolean; collapsed: boolean; onClick: () => void }) {
  return <button className={active ? 'nav-item active' : 'nav-item'} onClick={onClick} title={collapsed ? spaceLabels[item] : undefined}><Icon name={item} /><span>{spaceLabels[item]}</span></button>;
}

function Metric({ label, value }: { label: string; value: string | number }) { return <span>{label} <b>{value}</b></span>; }

function Home({ snapshot, navigate }: { snapshot: JarvisSnapshot; navigate: (space: Space) => void }) {
  const active = snapshot.projects.filter((project) => project.state === 'ACTIVE' || project.state === 'PAUSED');
  return <section className="home-grid">
    <div className="panel cockpit command-cockpit">
      <div className="panel-heading"><span>COMMAND CENTER</span><small>LIVE SYSTEM VIEW</small></div>
      <div className="cockpit-body"><div><span className="signal-label">WHAT JARVIS IS DOING</span><strong>{snapshot.currentFocus}</strong><p>{snapshot.attentionRequired ? snapshot.attentionReason : 'JARVIS is maintaining context, evaluating work and waiting for the next meaningful transition.'}</p><div className="cockpit-actions"><button className="primary-action" onClick={() => navigate('CONTROL')}>Open Mission Control →</button><button className="soft-action" onClick={() => navigate('CHAT')}>Talk to JARVIS</button></div></div><div className="signal-ring"><span>{snapshot.cognitiveActivity}</span><small>COGNITION</small></div></div>
      <div className="cockpit-footer"><span>CORE STATE · {modeLabels[snapshot.mode]}</span><b>{snapshot.lastStateChange}</b></div>
    </div>
    <div className={`panel attention ${snapshot.attentionRequired ? 'attention-hot' : ''}`}><div className="panel-kicker">ATTENTION</div><div className="attention-number">{snapshot.attentionRequired ? '01' : '00'}</div><div className="attention-copy">{snapshot.attentionReason}</div><button className="text-action" onClick={() => navigate('CONTROL')}>Open decision queue →</button></div>

    <div className="panel mission-glance wide">
      <div className="panel-heading"><span>MISSION FLOW</span><small>ORCHESTRATION MODEL</small></div>
      <div className="mission-flow"><FlowStep n="01" label="OBSERVE" detail="Context" active /><FlowLine /><FlowStep n="02" label="REASON" detail="Interpret" active={snapshot.mode === 'Thinking'} /><FlowLine /><FlowStep n="03" label="ASSIGN" detail="Model / agent" active={snapshot.mode === 'Working'} /><FlowLine /><FlowStep n="04" label="EXECUTE" detail="Capability" active={snapshot.mode === 'Working'} /><FlowLine /><FlowStep n="05" label="VERIFY" detail="Result" active={snapshot.mode === 'Learning'} /></div>
      <div className="mission-note"><span>DESIGNED FOR OBSERVABILITY</span><p>The interface is reserving explicit room for model reasoning summaries, delegation, tool usage, evidence and verification instead of hiding the process behind a single response bubble.</p></div>
    </div>

    <div className="panel work-overview"><div className="panel-heading"><span>WORK</span><small>{active.length} ACTIVE / HELD</small></div>{snapshot.projects.map((project) => <div className="project" key={project.id}><div><b>{project.name}</b><span>{project.state}</span></div>{typeof project.progress === 'number' && <div className="bar"><span style={{ width: `${project.progress}%` }} /></div>}</div>)}<button className="panel-action" onClick={() => navigate('WORK')}>Open work →</button></div>
    <div className="panel model-overview"><div className="panel-heading"><span>MODEL FLEET</span><small>ROLE / STATE</small></div>{snapshot.models.map((model) => <div className="model-row" key={model.id}><div><b>{model.name}</b><span>{model.role}</span></div><strong>{model.state}</strong></div>)}<button className="panel-action" onClick={() => navigate('SELF')}>Inspect runtime →</button></div>
    <div className="panel intelligence wide"><div className="panel-heading"><span>EVENT STREAM</span><small>LIVE TRACE</small></div><div className="activity-list">{snapshot.activity.map((item) => <div className="activity-item" key={item.id}><span className="activity-dot" /><div><b>{item.title}</b><p>{item.detail}</p></div><time>{item.timestamp}</time></div>)}</div></div>
    <div className="panel device-overview"><div className="panel-heading"><span>HOST</span><small>{snapshot.device.name}</small></div><div className="device-grid">{[['CPU', snapshot.device.cpu], ['MEMORY', snapshot.device.memory], ['GPU', snapshot.device.gpu], ['STORAGE', snapshot.device.storage]].map(([label, value]) => <div key={label}><span>{label}</span><b>{value}</b></div>)}</div></div>
    <div className="panel capability-overview"><div className="panel-heading"><span>CAPABILITY FABRIC</span><small>AVAILABLE</small></div><div className="cap-row"><span className="state-dot ready" /><b>Interface</b><span>READY</span></div><div className="cap-row"><span className="state-dot connected" /><b>GitHub</b><span>CONNECTED</span></div><div className="cap-row"><span className="state-dot online" /><b>Models</b><span>ONLINE</span></div><button className="panel-action" onClick={() => navigate('CAPABILITIES')}>Explore capabilities →</button></div>
  </section>;
}

function FlowStep({ n, label, detail, active }: { n: string; label: string; detail: string; active?: boolean }) { return <div className={`flow-step ${active ? 'active' : ''}`}><span>{n}</span><b>{label}</b><small>{detail}</small></div>; }
function FlowLine() { return <div className="flow-line"><i /></div>; }

function MissionControl({ snapshot, selectedProjectId, setSelectedProjectId, onOpenWork, onOpenChat }: { snapshot: JarvisSnapshot; selectedProjectId: string; setSelectedProjectId: (id: string) => void; onOpenWork: () => void; onOpenChat: () => void }) {
  const selected = snapshot.projects.find((project) => project.id === selectedProjectId) ?? snapshot.projects[0];
  const selectedWorkspace = snapshot.workspaces.find((workspace) => workspace.id === selected?.workspaceId);
  const assigned = snapshot.models.find((model) => model.state === 'ACTIVE') ?? snapshot.models[0];
  return <section className="space-panel panel mission-control">
    <div className="mission-control-head"><div><div className="panel-kicker">MISSION CONTROL · OBSERVABLE ORCHESTRATION</div><h1>See JARVIS work.</h1><p className="space-subtitle">The command surface for goals, model assignment, reasoning summaries, delegation, capabilities, evidence and verification. Live backend traces will eventually replace these structured preview states.</p></div><div className="mission-head-actions"><button className="soft-action" onClick={onOpenWork}>Open work</button><button className="primary-action" onClick={onOpenChat}>Give direction</button></div></div>
    <div className="mission-top-grid"><div className="mission-goal glass-card"><span>ACTIVE OBJECTIVE</span><b>{snapshot.currentFocus}</b><p>{selected?.detail ?? 'No project selected.'}</p><div className="goal-meta"><span>{selected?.state ?? 'IDLE'}</span><span>{selected?.progress ?? 0}% COMPLETE</span><span>{selectedWorkspace?.name ?? 'NO WORKSPACE'}</span></div></div><div className="mission-model glass-card"><span>ORCHESTRATOR LANE</span><div className="orchestrator-avatar">J</div><div><b>JARVIS Orchestrator</b><p>Coordinates context, model assignment and guarded progression.</p></div><span className="live-chip">{snapshot.resources.activeModelTasks ? 'ACTIVE' : 'STANDBY'}</span></div></div>
    <div className="mission-body-grid">
      <aside className="mission-project-list glass-card"><div className="subhead"><span>MISSIONS</span><small>{snapshot.projects.length}</small></div>{snapshot.projects.map((project) => <button key={project.id} className={project.id === selected.id ? 'mission-project selected' : 'mission-project'} onClick={() => setSelectedProjectId(project.id)}><span className={`mission-dot mission-${project.state.toLowerCase()}`} /><div><b>{project.name}</b><small>{project.currentAction ?? 'Awaiting procedure'}</small></div><em>{project.progress ?? 0}%</em></button>)}</aside>
      <div className="mission-center">
        <div className="glass-card pipeline-card"><div className="subhead"><span>ORCHESTRATION PIPELINE</span><small>GOAL → RESULT</small></div><div className="pipeline"><PipelineStage label="CONTEXT" detail="Load memory, project, workspace" state="complete" /><PipelineArrow /><PipelineStage label="REASON" detail={assigned?.detail ?? 'Interpret request and constraints'} state={snapshot.mode === 'Thinking' ? 'active' : 'ready'} /><PipelineArrow /><PipelineStage label="ASSIGN" detail={`${assigned?.name ?? 'Model'} · ${assigned?.role ?? 'reasoning'}`} state={snapshot.mode === 'Working' ? 'active' : 'ready'} /><PipelineArrow /><PipelineStage label="ACT" detail="Capabilities / tools / files" state={snapshot.mode === 'Working' ? 'active' : 'ready'} /><PipelineArrow /><PipelineStage label="VERIFY" detail="Evidence + result + continuation" state={snapshot.mode === 'Learning' ? 'active' : 'ready'} /></div></div>
        <div className="glass-card trace-card"><div className="subhead"><span>TRACE TIMELINE</span><small>{snapshot.selfActivity.length} EVENTS</small></div><div className="trace-list">{snapshot.selfActivity.slice(0, 6).map((item, index) => <div className="trace-event" key={item.id}><span className="trace-index">{String(index + 1).padStart(2, '0')}</span><span className={`trace-marker trace-${item.kind.toLowerCase()}`} /><div><b>{item.title}</b><p>{item.detail}</p></div><time>{item.timestamp}</time></div>)}</div></div>
      </div>
      <aside className="mission-inspector glass-card"><div className="subhead"><span>INSPECTOR</span><small>SELECTED WORK</small></div><div className="inspector-section"><span>WHY THIS MODEL</span><b>{assigned?.name ?? 'No model'}</b><p>{assigned?.detail ?? 'Waiting for a model assignment.'}</p></div><div className="inspector-section"><span>DECISION SUMMARY</span><b>{snapshot.mode === 'Thinking' ? 'Evaluate context before acting' : 'Maintain current procedure'}</b><p>Reasoning summaries belong here so the user can understand the decision without turning private chain-of-thought into an unsafe or misleading transcript.</p></div><div className="inspector-section"><span>BOUNDARIES</span><div className="boundary-row"><i /> Workspace <b>{selectedWorkspace?.name ?? 'Unassigned'}</b></div><div className="boundary-row"><i /> Resource <b>{snapshot.resources.strategy}</b></div><div className="boundary-row"><i /> Authority <b>CORE / POLICY</b></div></div><div className="inspector-section"><span>NEXT TRANSITION</span><b>{selected?.currentAction ?? 'Waiting for direction'}</b></div></aside>
    </div>
    <div className="mission-footnote"><span>PREVIEW STATE</span><p>These visuals define the interface contract. They do not claim to expose hidden model thoughts. The eventual backend should emit structured decision summaries, tool events, handoffs, evidence and verification records that can safely be rendered here.</p></div>
  </section>;
}

function PipelineStage({ label, detail, state }: { label: string; detail: string; state: 'complete' | 'active' | 'ready' }) { return <div className={`pipeline-stage ${state}`}><span>{state === 'complete' ? '✓' : state === 'active' ? '●' : '·'}</span><b>{label}</b><small>{detail}</small></div>; }
function PipelineArrow() { return <div className="pipeline-arrow">→</div>; }

function Chat({ surface, setSurface, history, composer, setComposer, submit, snapshot, selectedWorkspaceId, onSelectWorkspace, onSelectDirectory, selectedProjectId, setSelectedProjectId, navigate }: { surface: ChatSurface; setSurface: (surface: ChatSurface) => void; history: string[]; composer: string; setComposer: (value: string) => void; submit: () => void; snapshot: JarvisSnapshot; selectedWorkspaceId: string; onSelectWorkspace: (id: string) => void; onSelectDirectory: () => Promise<void>; selectedProjectId: string; setSelectedProjectId: (id: string) => void; navigate: (space: Space) => void }) {
  const activeWorkspace = snapshot.workspaces.find((workspace) => workspace.id === selectedWorkspaceId) ?? snapshot.workspaces[0];
  const activeProject = snapshot.projects.find((project) => project.id === selectedProjectId) ?? snapshot.projects[0];
  const definitions: Record<ChatSurface, { kicker: string; description: string; placeholder: string; tag: string }> = {
    CONVERSATION: { kicker: 'GENERAL INTELLIGENCE', description: 'General conversation with JARVIS. This is the natural-language front door to the whole environment.', placeholder: 'Talk to JARVIS...', tag: 'TALK' },
    WORKSPACE: { kicker: 'LITERAL WORKSPACE', description: 'A directory-rooted environment for inspection, generation, editing, coding and verification.', placeholder: `Command JARVIS in ${activeWorkspace?.name ?? 'this workspace'}...`, tag: 'BUILD' },
    RESEARCH: { kicker: 'ENGINEERING THINK TANK', description: 'Collect evidence, challenge assumptions, compare ideas and keep thoughts attached to material.', placeholder: 'Add a research direction, source, question or thought...', tag: 'THINK' },
    PLANNING: { kicker: 'PLANNING + AUTOMATION', description: 'Turn outcomes into plans, procedures and future automations without silently executing them.', placeholder: 'Describe an outcome or automation...', tag: 'PLAN' },
  };
  const active = definitions[surface];
  return <section className="chat-shell"><aside className="chat-sidebar panel"><div className="panel-kicker">CHAT SYSTEMS</div><button className="chat-new">+ New {chatLabels[surface].toLowerCase()}</button>{(Object.keys(chatLabels) as ChatSurface[]).map((item) => <button key={item} className={item === surface ? 'chat-mode active' : 'chat-mode'} onClick={() => setSurface(item)}><span>{chatLabels[item]}</span><small>{definitions[item].tag}</small></button>)}
    <div className="chat-toolbox history-box"><span className="panel-kicker">{surface === 'RESEARCH' ? 'RESEARCH HISTORY' : `${chatLabels[surface].toUpperCase()} HISTORY`}</span>{snapshot.chatHistory.filter((entry) => entry.surface === surface).map((entry) => <button className="history-item" key={entry.id}><b>{entry.title}</b><small>{entry.timestamp}</small><span>{entry.preview}</span></button>)}{history.length === 0 && <div className="history-empty">No local messages in this session.</div>}</div>
    {surface === 'WORKSPACE' && <div className="chat-toolbox"><span className="panel-kicker">WORKSPACE ROOT</span>{snapshot.workspaces.map((workspace) => <button className={`workspace-item ${workspace.id === selectedWorkspaceId ? 'selected' : ''}`} onClick={() => onSelectWorkspace(workspace.id)} key={workspace.id}><b>{workspace.name}</b><small>{workspace.path}</small></button>)}<button className="soft-action" onClick={() => void onSelectDirectory()}>+ Select directory</button><div className="workspace-project-link"><span>ACTIVE WORK</span><button onClick={() => navigate('WORK')}>{activeProject.name}</button></div></div>}
    {surface === 'RESEARCH' && <div className="chat-toolbox"><span className="panel-kicker">TOPICS</span>{snapshot.researchTopics.map((topic) => <button className={`research-topic ${topic.state === 'ACTIVE' ? 'selected' : ''}`} key={topic.id}><b>{topic.title}</b><small>{topic.state} · {topic.sourceCount} sources · {topic.thoughtCount} thoughts</small></button>)}</div>}
    {surface === 'PLANNING' && <div className="chat-toolbox"><span className="panel-kicker">PLANS</span>{snapshot.plans.map((plan) => <button className="plan-item" key={plan.id}><b>{plan.title}</b><small>{plan.state}{plan.automation ? ` · ${plan.automation}` : ''}</small></button>)}</div>}
  </aside><section className="panel chat-main"><div className="chat-header"><div><span className="panel-kicker">{active.kicker}</span><h1>{chatLabels[surface]}</h1><p>{active.description}</p></div><button className="chat-orchestrate" onClick={() => navigate('CONTROL')}>VIEW ORCHESTRATION →</button></div>
    {surface === 'CONVERSATION' && <div className="chat-history">{history.length === 0 ? <div className="chat-empty"><span className="empty-orb" /><h2>Enter JARVIS.</h2><p>Conversation is the front door. From here, JARVIS can route into work, research, planning or deeper system coordination.</p></div> : history.map((message, index) => <div className="chat-message" key={`${message}-${index}`}><span>YOU</span><p>{message}</p></div>)}</div>}
    {surface === 'WORKSPACE' && <WorkspaceSurface workspace={activeWorkspace} />}
    {surface === 'RESEARCH' && <ResearchSurface snapshot={snapshot} />}
    {surface === 'PLANNING' && <PlanningSurface snapshot={snapshot} />}
    <div className="chat-composer"><textarea value={composer} onChange={(event) => setComposer(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit(); } }} placeholder={active.placeholder} /><button onClick={submit} aria-label="Send command">↑</button></div>
  </section></section>;
}

function WorkspaceSurface({ workspace }: { workspace?: JarvisSnapshot['workspaces'][number] }) { return <div className="special-surface"><div className="workspace-banner"><div><span className="surface-label">WORKSPACE ROOT</span><h2>{workspace?.name ?? 'No workspace selected'}</h2><p>{workspace?.path ?? 'Select a directory to give this workspace a root.'}</p></div><span className="surface-state">{workspace?.status ?? 'AVAILABLE'}</span></div><div className="workspace-grid">{[['INSPECT', 'Understand before changing', 'JARVIS should establish workspace context first.'], ['GENERATE', 'Build inside the root', 'Code and artifacts belong to this explicit project space.'], ['EDIT', 'Modify existing work', 'Changes remain tied to project and workspace context.'], ['VERIFY', 'Prove the result', 'Tests, diffs and resulting state should be visible.']].map(([label, title, detail]) => <div className="surface-card" key={label}><span>{label}</span><b>{title}</b><p>{detail}</p></div>)}</div></div>; }
function ResearchSurface({ snapshot }: { snapshot: JarvisSnapshot }) { const thoughtOn = snapshot.researchTopics.filter((topic) => topic.state === 'THOUGHT_ON'); return <div className="special-surface"><div className="research-command"><div><span className="surface-label">THINK TANK</span><h2>Think with the material.</h2><p>Research stays distinct from thought, so evidence can be revisited rather than becoming hidden context.</p></div><span className="surface-state">{thoughtOn.length} THOUGHT ON</span></div><div className="research-board">{snapshot.researchTopics.map((topic) => <article className="research-card" key={topic.id}><div className="research-card-top"><span>{topic.state}</span><button>THINK →</button></div><h3>{topic.title}</h3><p>{topic.detail}</p><div className="research-footer"><span>{topic.sourceCount} SOURCES · {topic.thoughtCount} THOUGHTS</span><b>{topic.lastThought ?? 'Waiting for deeper thought.'}</b></div></article>)}</div></div>; }
function PlanningSurface({ snapshot }: { snapshot: JarvisSnapshot }) { return <div className="special-surface"><div className="planning-command"><span className="surface-label">PLANNING + AUTOMATION</span><h2>Prepare JARVIS to execute.</h2><p>A plan can become work, research, monitoring or recurring automation after the appropriate authority boundaries accept it.</p></div><div className="plan-board">{snapshot.plans.map((plan) => <article className="plan-card" key={plan.id}><div className="plan-card-top"><span>{plan.state}</span><b>{plan.steps.length} STEPS</b></div><h3>{plan.title}</h3>{plan.automation && <div className="automation-label">AUTOMATION · {plan.automation}</div>}{plan.steps.map((step, index) => <div className={`plan-step ${plan.currentStep === index + 1 ? 'current' : ''}`} key={step}><span>{index + 1}</span>{step}</div>)}</article>)}</div></div>; }

function Projects({ snapshot, selectedProjectId, setSelectedProjectId, controlProject, onNavigate }: { snapshot: JarvisSnapshot; selectedProjectId: string; setSelectedProjectId: (id: string) => void; controlProject: (id: string, state: Extract<ProjectState, 'ACTIVE' | 'PAUSED'>) => Promise<void>; onNavigate: (space: Space) => void }) {
  const selected = snapshot.projects.find((project) => project.id === selectedProjectId) ?? snapshot.projects[0];
  const workspace = snapshot.workspaces.find((item) => item.id === selected?.workspaceId);
  return <section className="space-panel panel"><div className="work-control-head"><div><div className="panel-kicker">WORK · PROJECT CONTROL</div><h1>{selected?.name ?? 'Work'}</h1><p className="space-subtitle">A living work object: context, workspace, plan, model assignment, feedback and runtime state all belong to one place.</p></div><div className="work-head-actions"><button className="soft-action" onClick={() => onNavigate('CONTROL')}>Mission Control</button><button className="primary-action" onClick={() => onNavigate('CHAT')}>Create through Chat →</button></div></div><div className="project-control-layout"><aside className="project-list glass-rail">{snapshot.projects.map((project) => <button key={project.id} className={project.id === selected?.id ? 'project-select active' : 'project-select'} onClick={() => setSelectedProjectId(project.id)}><span>{project.state}</span><b>{project.name}</b><small>{project.progress ?? 0}% · {project.currentAction ?? 'No current action'}</small></button>)}</aside><div className="project-detail"><div className="work-runtime"><div><span className="surface-label">RUNTIME STATE</span><strong>{selected?.state ?? 'IDLE'}</strong><p>{selected?.detail ?? 'Project context is being maintained.'}</p><div className="runtime-meta"><span>WORKSPACE · {workspace?.name ?? 'UNASSIGNED'}</span><span>MODEL · {snapshot.models.find((model) => model.state === 'ACTIVE')?.name ?? 'STANDBY'}</span></div></div><button className={`control-toggle ${selected?.state === 'PAUSED' ? 'paused' : ''}`} disabled={selected?.state !== 'ACTIVE' && selected?.state !== 'PAUSED'} onClick={() => selected && void controlProject(selected.id, selected.state === 'ACTIVE' ? 'PAUSED' : 'ACTIVE')}><span />{selected?.state === 'PAUSED' ? 'RESUME' : 'PAUSE'}</button></div><div className="project-detail-grid"><div className="surface-card project-highlight"><span>PROGRESS</span><b>{selected?.progress ?? 0}%</b>{typeof selected?.progress === 'number' && <div className="bar"><span style={{ width: `${selected.progress}%` }} /></div>}<p>{selected?.currentAction ?? 'No active operation.'}</p></div><div className="surface-card"><span>WORKSPACE</span><b>{workspace?.name ?? 'Not assigned'}</b><p>{workspace?.path ?? 'Select a workspace in Chat.'}</p></div><div className="surface-card"><span>ORCHESTRATION</span><b>{snapshot.mode}</b><p>{snapshot.selfActivity[0]?.detail ?? 'No active trace.'}</p></div><div className="surface-card"><span>BOUNDARIES</span><b>CORE / POLICY</b><p>Project control remains separate from authorization and execution authority.</p></div></div></div></div></section>;
}

function Mind({ snapshot, onOpenControl }: { snapshot: JarvisSnapshot; onOpenControl: () => void }) {
  const [view, setView] = useState<'EXPLORER' | 'GRAPH' | 'THINKING'>('EXPLORER');
  const [selectedRoot, setSelectedRoot] = useState('Memory');
  const roots = [['Memory','Stored context, facts and durable experience.'],['Thinking','Active reasoning, questions and working context.'],['Plans','Outcomes, procedures and future actions.'],['Learning','Evaluation, adaptation and reliability signals.'],['Relationships','People, systems, concepts and their connections.'],['Projects','Work objects connected to workspace and plans.'],['Knowledge','Organized information and evidence.'],['Experiences','What JARVIS has encountered and learned from.'],['Preferences','Stable user and system preferences.'],['Goals','Longer-horizon objectives and direction.'],['Skills','Capabilities JARVIS can develop or invoke.'],['Workflows','Repeatable procedures and automation patterns.']];
  const root = roots.find(([name]) => name === selectedRoot) ?? roots[0];
  return <section className="space-panel panel mind-core-panel"><div className="panel-kicker">MIND CORE · INTERNAL WORLD</div><div className="space-heading-row"><div><h1>Mind</h1><p className="space-subtitle">Memory, thought, knowledge, experience, plans and relationships—shown as an environment rather than a generic dashboard.</p></div><div className="mind-header-actions"><button className="soft-action" onClick={onOpenControl}>See orchestration</button><div className="segmented"><button className={view === 'EXPLORER' ? 'active' : ''} onClick={() => setView('EXPLORER')}>Explorer</button><button className={view === 'GRAPH' ? 'active' : ''} onClick={() => setView('GRAPH')}>Graph</button><button className={view === 'THINKING' ? 'active' : ''} onClick={() => setView('THINKING')}>Thinking</button></div></div></div>
    {view === 'EXPLORER' && <div className="mind-explorer-layout"><aside className="mind-root-list">{roots.map(([name, detail]) => <button key={name} className={selectedRoot === name ? 'mind-root active' : 'mind-root'} onClick={() => setSelectedRoot(name)}><span>◈</span><div><b>{name}</b><small>{detail}</small></div></button>)}</aside><div className="mind-root-detail"><div className="mind-context-banner"><span>SELECTED DOMAIN</span><strong>{root[0]}</strong><p>{root[1]}</p></div><div className="mind-stat-grid"><div><span>ACTIVE CONTEXT</span><b>{snapshot.currentFocus}</b></div><div><span>WORK</span><b>{snapshot.projects.length}</b></div><div><span>RESEARCH</span><b>{snapshot.researchTopics.length}</b></div><div><span>PLANS</span><b>{snapshot.plans.length}</b></div></div><div className="surface-card mind-detail-card"><span>DOMAIN STATE</span><b>{root[0]} is a first-class Mind domain</b><p>Selecting a domain should eventually open its real records, provenance, relationships, history and permitted operations.</p></div></div></div>}
    {view === 'GRAPH' && <div className="relationship-map mind-graph"><span className="node center">MIND CORE</span><span className="node n1">MEMORY</span><span className="node n2">THINKING</span><span className="node n3">PLANS</span><span className="node n4">LEARNING</span><span className="node n5">PROJECTS</span><span className="node n6">RELATIONSHIPS</span>{['c1','c2','c3','c4','c5','c6'].map((item) => <div className={`connection ${item}`} key={item} />)}</div>}
    {view === 'THINKING' && <div className="mind-thinking-grid"><div className="surface-card mind-active-thought"><span>ACTIVE CONTEXT</span><b>{snapshot.currentFocus}</b><p>Current context JARVIS is carrying into its cognitive loop.</p><button className="text-action" onClick={onOpenControl}>Inspect orchestration →</button></div>{snapshot.researchTopics.map((topic) => <div className="surface-card" key={topic.id}><span>{topic.state}</span><b>{topic.title}</b><p>{topic.lastThought ?? 'Awaiting deeper thought.'}</p></div>)}</div>}
    <div className="mind-foot"><span>CORE · {view}</span><b>{roots.length} domains · {snapshot.projects.length} work · {snapshot.researchTopics.length} research roots · {snapshot.plans.length} plans</b></div>
  </section>;
}

function Capabilities({ snapshot }: { snapshot: JarvisSnapshot }) { return <section className="space-panel panel"><div className="panel-kicker">CAPABILITY FABRIC</div><h1>Capabilities</h1><p className="space-subtitle">Every model, plugin, integration, worker, skill, device and automation should become something JARVIS can identify, explain, scope and eventually invoke.</p><div className="capability-grid">{snapshot.capabilities.map((capability) => <div className="capability-card" key={capability.id}><div><span className={`state-dot ${capability.state.toLowerCase()}`} /><b>{capability.name}</b><span>{capability.state}</span></div><p>{capability.detail}</p></div>)}</div><div className="expansion-rail"><span>SELF-BUILDING FABRIC</span><b>MODELS · PLUGINS · INTEGRATIONS · WORKERS · SKILLS · DEVICES · AUTOMATIONS</b><p>Capability discovery, testing, explanation and scoped use belong here instead of being scattered across the application.</p></div></section>; }

function Self({ snapshot, onOpenControl }: { snapshot: JarvisSnapshot; onOpenControl: () => void }) { return <section className="space-panel panel"><div className="panel-kicker">SELF OBSERVATION</div><div className="self-head"><div><h1>Self</h1><p className="space-subtitle">See how JARVIS allocates models, reacts to pressure and exposes internal runtime state without confusing observation with authority.</p></div><div className={`self-pressure pressure-${snapshot.resources.pressure.toLowerCase()}`}><span>{snapshot.resources.pressure}</span><b>{snapshot.resources.strategy.replace('_',' ')}</b></div></div><div className="self-runtime"><div className="resource-meters">{[['CPU', snapshot.resources.cpuLoad], ['MEMORY', snapshot.resources.memoryLoad], ['GPU', snapshot.resources.gpuLoad]].map(([label, value]) => <div key={label}><span>{label}</span><b>{value}%</b><div className="resource-bar"><i style={{ width: `${value}%` }} /></div></div>)}</div><div className="delegation-state"><span className="surface-label">MODEL COORDINATION</span><strong>{snapshot.resources.activeModelTasks} ACTIVE TASK</strong><p>{snapshot.resources.concurrencyLimit === 1 ? 'Sequential model handoff is active.' : 'Limited parallel model work is available.'}</p><button className="soft-action" onClick={onOpenControl}>Open Mission Control →</button></div></div><div className="self-activity"><div className="panel-heading"><span>JARVIS ACTIVITY</span><small>LIVE INTERNAL VIEW</small></div>{snapshot.selfActivity.map((item) => <div className="self-activity-row" key={item.id}><span className={`self-activity-icon self-${item.kind.toLowerCase()}`}><i /></span><div><b>{item.title}</b><p>{item.detail}</p></div><div className="self-model">{item.modelId ? snapshot.models.find((model) => model.id === item.modelId)?.name ?? item.modelId : 'JARVIS'}<small>{item.timestamp}</small></div></div>)}</div><div className="self-grid">{[['Architecture','Core authority remains backend-owned.'],['Mind','Internal context, memory and relationships are represented separately.'],['Learning','Learning signals remain distinct from truth and authority.'],['Models',`${snapshot.models.length} model roles are represented.`],['Capabilities',`${snapshot.capabilities.length} currently known capabilities.`],['Resource policy','JARVIS observes system pressure before increasing model concurrency.']].map(([title, detail]) => <div className="self-card" key={title}><span>{title}</span><p>{detail}</p></div>)}</div></section>; }

function CommandPalette({ close, navigate, snapshot }: { close: () => void; navigate: (space: Space) => void; snapshot: JarvisSnapshot }) {
  const commands: { label: string; detail: string; target: Space }[] = [
    { label: 'Open Home', detail: 'Command center and orientation', target: 'HOME' },
    { label: 'Open Chat', detail: 'Talk, build, research or plan', target: 'CHAT' },
    { label: 'Open Work', detail: 'Projects and runtime control', target: 'WORK' },
    { label: 'Open Mission Control', detail: 'Observe orchestration and traces', target: 'CONTROL' },
    { label: 'Open Mind', detail: 'Memory, thought, plans and relationships', target: 'MIND' },
    { label: 'Open Capabilities', detail: 'Models, plugins and tools', target: 'CAPABILITIES' },
    { label: 'Open Self', detail: 'Runtime, resources and model coordination', target: 'SELF' },
  ];
  return <div className="command-overlay" onMouseDown={close}><div className="command-palette" onMouseDown={(event) => event.stopPropagation()}><div className="command-head"><span>JARVIS COMMAND</span><kbd>ESC</kbd></div><div className="command-input-wrap"><span>⌕</span><input autoFocus placeholder="Navigate the JARVIS environment..." /></div><div className="command-list">{commands.map((command, index) => <button key={command.target} onClick={() => navigate(command.target)}><span className="command-key">{String(index + 1).padStart(2,'0')}</span><div><b>{command.label}</b><small>{command.detail}</small></div><em>{spaceLabels[command.target]}</em></button>)}</div><div className="command-foot"><span>CORE STATUS · {snapshot.online ? 'CONNECTED' : 'OFFLINE'}</span><span>{snapshot.resources.pressure} PRESSURE</span><span>CTRL K</span></div></div></div>;
}

export default App;
