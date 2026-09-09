import { useMemo, useState } from 'react';
import { initialSnapshot, type JarvisSnapshot } from './contracts';

const spaces = ['HOME', 'WORK', 'MIND', 'CAPABILITIES', 'SELF'] as const;

type Space = typeof spaces[number];

function App() {
  const [space, setSpace] = useState<Space>('HOME');
  const [composer, setComposer] = useState('');
  const [messages, setMessages] = useState<string[]>([]);
  const [snapshot] = useState<JarvisSnapshot>(initialSnapshot);

  const current = useMemo(() => ({ ...snapshot, mode: space === 'WORK' ? 'Working' : snapshot.mode }), [snapshot, space]);

  const submit = () => {
    const value = composer.trim();
    if (!value) return;
    setMessages((items) => [...items, value]);
    setComposer('');
    setSpace('HOME');
  };

  return (
    <div className="shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />

      <header className="topbar">
        <div className="brand"><span className="brand-mark">J</span><span>JARVIS</span></div>
        <div className="presence"><span className="pulse" /> {current.online ? 'ONLINE' : 'OFFLINE'}</div>
        <div className="top-meta">COGNITIVE ACTIVITY <strong>{current.cognitiveActivity}</strong></div>
      </header>

      <main className="layout">
        <section className="hero">
          <div className="hero-title">{current.mode}</div>
          <div className="hero-focus">{current.currentFocus}</div>
          <div className="hero-metrics">
            <span>CAPABILITIES <b>{current.activeCapabilities}</b></span>
            <span>SOURCES <b>{current.monitoredSources}</b></span>
          </div>
        </section>

        <nav className="spaces" aria-label="JARVIS spaces">
          {spaces.map((item) => (
            <button key={item} className={item === space ? 'space active' : 'space'} onClick={() => setSpace(item)}>
              {item}
            </button>
          ))}
        </nav>

        {space === 'HOME' && (
          <section className="home-grid">
            <div className="panel conversation wide">
              <div className="panel-kicker">CONVERSATIONAL WORKSPACE</div>
              <div className="conversation-body">
                <div className="greeting">What are you working on?</div>
                {messages.length > 0 && <div className="message-stack">{messages.map((m, i) => <div className="user-message" key={`${m}-${i}`}>{m}</div>)}</div>}
                <div className="composer">
                  <input value={composer} onChange={(e) => setComposer(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && submit()} placeholder="Talk to JARVIS..." />
                  <button onClick={submit}>→</button>
                </div>
              </div>
            </div>

            <div className="panel focus">
              <div className="panel-kicker">CURRENT FOCUS</div>
              <div className="focus-value">{current.currentFocus}</div>
              <div className="focus-mode">{current.mode.toUpperCase()}</div>
            </div>

            <div className="panel intelligence wide">
              <div className="panel-heading"><span>RECENT INTELLIGENCE</span><small>ACTIVITY</small></div>
              <div className="activity-list">{current.activity.map((item) => <div className="activity-item" key={item.id}><span className="activity-dot" /><div><b>{item.title}</b><p>{item.detail}</p></div><time>{item.timestamp}</time></div>)}</div>
            </div>

            <div className="panel projects">
              <div className="panel-kicker">PROJECTS</div>
              {current.projects.map((project) => <div className="project" key={project.id}><div><b>{project.name}</b><span>{project.state}</span></div>{typeof project.progress === 'number' && <div className="bar"><span style={{ width: `${project.progress}%` }} /></div>}</div>)}
            </div>
          </section>
        )}

        {space === 'WORK' && <SpacePanel title="WORK" subtitle="Everything JARVIS is currently doing." items={current.projects.map((p) => `${p.name} · ${p.state}${p.progress ? ` · ${p.progress}%` : ''}`)} />}
        {space === 'MIND' && <SpacePanel title="MIND" subtitle="Memory and knowledge will become a visible second brain." items={['Personal', 'Skills', 'Preferences', 'Projects', 'Goals', 'Facts', 'Workflows', 'Relationships', 'Experiences', 'Knowledge graph']} />}
        {space === 'CAPABILITIES' && <SpacePanel title="CAPABILITIES" subtitle="The third hand: declared abilities and their current state." items={current.capabilities.map((c) => `${c.name} · ${c.state} · ${c.detail ?? ''}`)} />}
        {space === 'SELF' && <SpacePanel title="SELF" subtitle="JARVIS explaining its own architecture and condition." items={['Architecture', 'Capabilities', 'Versions', 'Performance', 'Memory', 'Learning', 'Security', 'Health', 'Updates', 'Experiments']} />}
      </main>
    </div>
  );
}

function SpacePanel({ title, subtitle, items }: { title: string; subtitle: string; items: string[] }) {
  return <section className="space-panel panel"><div className="panel-kicker">{title}</div><h1>{title}</h1><p className="space-subtitle">{subtitle}</p><div className="space-items">{items.map((item) => <div className="space-row" key={item}><span className="row-orb" />{item}<span>›</span></div>)}</div></section>;
}

export default App;