import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisMode, JarvisSnapshot } from './contracts';

const spaces = ['HOME', 'CHAT', 'WORK', 'MIND', 'CAPABILITIES', 'SELF'] as const;
type Space = typeof spaces[number];

const modeLabels: Record<JarvisMode, string> = {
  Thinking: 'COGNITIVE LOOP',
  Learning: 'LEARNING',
  Working: 'WORKING',
  Monitoring: 'MONITORING',
  Waiting: 'STANDING BY',
  'Needs You': 'ATTENTION REQUIRED',
};

function App() {
  const [space, setSpace] = useState<Space>('HOME');
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [composer, setComposer] = useState('');
  const [chat, setChat] = useState<string[]>([]);
  const [lastEvent, setLastEvent] = useState('System initialized');

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
    const event = await demoGateway.submit({ text: value, sessionId: 'desktop' });
    setLastEvent(event.title);
    setSnapshot(demoGateway.snapshotSync());
  };

  return (
    <div className={`shell mode-${snapshot.mode.toLowerCase().replace(/\s+/g, '-').replace('you', 'you')}`}>
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="ambient-core" aria-hidden="true"><span /></div>

      <header className="topbar">
        <button className="brand" onClick={() => setSpace('HOME')} aria-label="Return to JARVIS Home">
          <span className="brand-mark">J</span><span>JARVIS</span>
        </button>
        <div className="presence"><span className="pulse" />{snapshot.online ? 'ONLINE' : 'OFFLINE'}<span className="presence-detail">{current.modeLabel}</span></div>
        <div className="top-meta">COGNITIVE ACTIVITY <strong>{current.cognitiveActivity}</strong><span className="top-separator">·</span>UPTIME <strong>{snapshot.uptime}</strong></div>
      </header>

      <main className="layout">
        <section className="hero">
          <div className="hero-eyebrow">JARVIS SYSTEM STATE</div>
          <div className="hero-title">{snapshot.mode}</div>
          <div className="hero-focus">{snapshot.currentFocus}</div>
          <div className="hero-metrics">
            <Metric label="CAPABILITIES" value={snapshot.activeCapabilities} />
            <Metric label="SOURCES" value={snapshot.monitoredSources} />
            <Metric label="ACTIVE WORK" value={snapshot.activeWork} />
            <Metric label="ATTENTION" value={snapshot.attentionRequired ? 'YES' : 'CLEAR'} />
          </div>
          <div className="live-strip"><span className="live-dot" /> LIVE · {lastEvent}</div>
        </section>

        <nav className="spaces" aria-label="JARVIS spaces">
          {spaces.map((item) => (
            <button key={item} className={item === space ? 'space active' : 'space'} onClick={() => setSpace(item)}>
              {item}
            </button>
          ))}
        </nav>

        {space === 'HOME' && <Home snapshot={snapshot} onNavigate={setSpace} />}
        {space === 'CHAT' && <Chat chat={chat} composer={composer} setComposer={setComposer} submit={submit} snapshot={snapshot} />}
        {space === 'WORK' && <Work snapshot={snapshot} />}
        {space === 'MIND' && <Mind snapshot={snapshot} />}
        {space === 'CAPABILITIES' && <Capabilities snapshot={snapshot} />}
        {space === 'SELF' && <Self snapshot={snapshot} />}
      </main>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return <span>{label} <b>{value}</b></span>;
}

function Home({ snapshot, onNavigate }: { snapshot: JarvisSnapshot; onNavigate: (space: Space) => void }) {
  return <section className="home-grid">
    <div className="panel cockpit">
      <div className="panel-kicker">LIVE COCKPIT</div>
      <div className="cockpit-body">
        <div><span className="signal-label">CURRENT FOCUS</span><strong>{snapshot.currentFocus}</strong><p>{snapshot.mode === 'Needs You' ? 'JARVIS is waiting for your decision.' : 'System is observing, reasoning, and maintaining current context.'}</p></div>
        <div className="signal-ring"><span>{snapshot.cognitiveActivity}</span><small>COGNITION</small></div>
      </div>
      <div className="cockpit-footer"><span>Last state change</span><b>{snapshot.lastStateChange}</b></div>
    </div>

    <div className={`panel attention ${snapshot.attentionRequired ? 'attention-hot' : ''}`}>
      <div className="panel-kicker">ATTENTION</div>
      <div className="attention-number">{snapshot.attentionRequired ? 'YES' : 'CLEAR'}</div>
      <div className="attention-copy">{snapshot.attentionReason}</div>
      <button className="text-action" onClick={() => onNavigate('WORK')}>Review work →</button>
    </div>

    <div className="panel intelligence wide">
      <div className="panel-heading"><span>RECENT INTELLIGENCE</span><small>LIVE STREAM</small></div>
      <div className="activity-list">{snapshot.activity.map((item) => <div className="activity-item" key={item.id}><span className="activity-dot" /><div><b>{item.title}</b><p>{item.detail}</p></div><time>{item.timestamp}</time></div>)}</div>
    </div>

    <div className="panel work-overview">
      <div className="panel-heading"><span>WORK</span><small>{snapshot.activeWork} ACTIVE</small></div>
      {snapshot.projects.map((project) => <div className="project" key={project.id}><div><b>{project.name}</b><span>{project.state}</span></div>{typeof project.progress === 'number' && <div className="bar"><span style={{ width: `${project.progress}%` }} /></div>}</div>)}
      <button className="panel-action" onClick={() => onNavigate('WORK')}>Open workspace →</button>
    </div>

    <div className="panel capability-overview">
      <div className="panel-heading"><span>CAPABILITY FABRIC</span><small>LIVE</small></div>
      {snapshot.capabilities.slice(0, 5).map((cap) => <div className="cap-row" key={cap.id}><span className={`state-dot ${cap.state.toLowerCase()}`} /><b>{cap.name}</b><span>{cap.state}</span></div>)}
      <button className="panel-action" onClick={() => onNavigate('CAPABILITIES')}>Open capabilities →</button>
    </div>
  </section>;
}

function Chat({ chat, composer, setComposer, submit, snapshot }: { chat: string[]; composer: string; setComposer: (v: string) => void; submit: () => void; snapshot: JarvisSnapshot }) {
  const modes = ['Conversation', 'Workspace', 'Research', 'Planning'] as const;
  const [chatMode, setChatMode] = useState<(typeof modes)[number]>('Conversation');
  return <section className="chat-shell">
    <aside className="chat-sidebar panel">
      <div className="panel-kicker">CHAT MAP</div>
      <button className="chat-new">+ New conversation</button>
      {modes.map((mode) => <button key={mode} className={mode === chatMode ? 'chat-mode active' : 'chat-mode'} onClick={() => setChatMode(mode)}>{mode}<span>›</span></button>)}
      <div className="chat-context"><span className="panel-kicker">ACTIVE CONTEXT</span><b>{snapshot.currentFocus}</b><p>HOME state, work state, capabilities and relevant memory can be referenced here.</p></div>
    </aside>
    <section className="panel chat-main">
      <div className="chat-header"><div><span className="panel-kicker">{chatMode.toUpperCase()}</span><h1>{chatMode}</h1></div><span className="chat-status"><i /> context-aware</span></div>
      <div className="chat-history">{chat.length === 0 ? <div className="chat-empty"><span className="empty-orb" /><h2>Talk to JARVIS.</h2><p>Reference the live cockpit, projects, memory, research and capabilities from one conversation space.</p></div> : chat.map((message, index) => <div className="chat-message" key={`${message}-${index}`}><span>YOU</span><p>{message}</p></div>)}</div>
      <div className="chat-composer"><textarea value={composer} onChange={(e) => setComposer(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } }} placeholder={`Message JARVIS · ${chatMode.toLowerCase()}`} /><button onClick={submit}>↑</button></div>
    </section>
  </section>;
}

function Work({ snapshot }: { snapshot: JarvisSnapshot }) {
  return <section className="space-panel panel"><div className="panel-kicker">WORK CONTROL</div><h1>Work</h1><p className="space-subtitle">Active work, progress, waiting conditions, and long-running execution state.</p><div className="work-grid">{snapshot.projects.map((project) => <div className="work-card" key={project.id}><div className="work-card-top"><span>{project.state}</span>{typeof project.progress === 'number' && <b>{project.progress}%</b>}</div><h3>{project.name}</h3><p>{project.state === 'WAITING' ? 'Waiting for a condition or external input.' : 'JARVIS is maintaining context and progress.'}</p>{typeof project.progress === 'number' && <div className="bar"><span style={{ width: `${project.progress}%` }} /></div>}</div>)}</div></section>;
}

function Mind({ snapshot }: { snapshot: JarvisSnapshot }) {
  const [view, setView] = useState<'FOLDERS' | 'RELATIONSHIPS'>('FOLDERS');
  const folders = ['Personal', 'Skills', 'Preferences', 'Projects', 'Goals', 'Facts', 'Workflows', 'Relationships', 'Experiences'];
  return <section className="space-panel panel"><div className="panel-kicker">SECOND BRAIN</div><div className="space-heading-row"><div><h1>Mind</h1><p className="space-subtitle">Memory and knowledge as a navigable system.</p></div><div className="segmented"><button className={view === 'FOLDERS' ? 'active' : ''} onClick={() => setView('FOLDERS')}>Folders</button><button className={view === 'RELATIONSHIPS' ? 'active' : ''} onClick={() => setView('RELATIONSHIPS')}>Relationships</button></div></div>{view === 'FOLDERS' ? <div className="folder-grid">{folders.map((folder) => <div className="folder" key={folder}><span>◈</span><b>{folder}</b><small>evidence-aware</small></div>)}</div> : <div className="relationship-map"><span className="node center">JARVIS</span><span className="node n1">PROJECTS</span><span className="node n2">SKILLS</span><span className="node n3">GOALS</span><span className="node n4">EXPERIENCES</span><span className="node n5">RELATIONSHIPS</span><div className="connection c1" /><div className="connection c2" /><div className="connection c3" /><div className="connection c4" /><div className="connection c5" /></div>}<div className="mind-foot"><span>Evidence model: ready for live memory</span><b>{snapshot.projects.length} project roots</b></div></section>;
}

function Capabilities({ snapshot }: { snapshot: JarvisSnapshot }) {
  return <section className="space-panel panel"><div className="panel-kicker">CAPABILITY FABRIC</div><h1>Capabilities</h1><p className="space-subtitle">The third hand: tools, models and integrations are visible here without gaining authority.</p><div className="capability-grid">{snapshot.capabilities.map((cap) => <div className="capability-card" key={cap.id}><div><span className={`state-dot ${cap.state.toLowerCase()}`} /><b>{cap.name}</b><span>{cap.state}</span></div><p>{cap.detail}</p></div>)}</div></section>;
}

function Self({ snapshot }: { snapshot: JarvisSnapshot }) {
  return <section className="space-panel panel"><div className="panel-kicker">SELF OBSERVATION</div><h1>Self</h1><p className="space-subtitle">JARVIS should be able to explain itself until you understand it.</p><div className="self-grid">{[['Architecture','Core authority remains backend-owned.'],['Runtime','Live state is available through the gateway boundary.'],['Memory','Evidence-aware knowledge is visible to the user.'],['Learning','Learning signals remain separate from truth and authority.'],['Security','The security model will become a dedicated hardening phase.'],['Performance',`Current focus: ${snapshot.currentFocus}`],['Updates','Changes should be explainable and verified.'],['Experiments','Experimental capabilities remain visibly distinct.']].map(([title, detail]) => <div className="self-card" key={title}><span>{title}</span><p>{detail}</p></div>)}</div></section>;
}

export default App;