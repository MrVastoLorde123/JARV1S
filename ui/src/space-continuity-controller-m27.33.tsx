import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type Space = 'HOME' | 'CHAT' | 'WORK' | 'CONTROL' | 'MIND' | 'CAPABILITIES' | 'SELF';

const spaces: Array<{ id: Space; detail: string }> = [
  { id: 'HOME', detail: 'orientation' }, { id: 'CHAT', detail: 'intent' }, { id: 'WORK', detail: 'execution' },
  { id: 'CONTROL', detail: 'authority' }, { id: 'MIND', detail: 'context' }, { id: 'CAPABILITIES', detail: 'power' }, { id: 'SELF', detail: 'runtime' },
];

function openSpace(space: Space) {
  const button = Array.from(document.querySelectorAll<HTMLButtonElement>('.nav-item')).find((item) => item.textContent?.trim() === space);
  button?.click();
}

function ContinuityRail({ snapshot }: { snapshot: JarvisSnapshot }) {
  const [active, setActive] = useState<Space>('HOME');

  useEffect(() => {
    const sync = () => {
      const shell = document.querySelector<HTMLElement>('.shell');
      const current = shell?.dataset.space as Space | undefined;
      const navCurrent = document.querySelector('.nav-item.active')?.textContent?.trim() as Space | undefined;
      const next = current ?? navCurrent;
      if (next) setActive(next);
    };
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const mission = snapshot.projects.find((project) => project.state === 'ACTIVE') ?? snapshot.projects[0];
  return <nav className="space-continuity-rail" aria-label="JARVIS operating instruments">
    {spaces.map((space, index) => (
      <button key={space.id} className={`space-continuity-link ${active === space.id ? 'active' : ''}`} onClick={() => { setActive(space.id); openSpace(space.id); }}>
        <span className="space-continuity-index">{String(index + 1).padStart(2, '0')}</span>
        <span className="space-continuity-copy"><b>{space.id}</b><small>{space.detail}{active === space.id ? ` · ${mission?.name ?? snapshot.currentFocus}` : ''}</small></span>
      </button>
    ))}
  </nav>;
}

export function installSpaceContinuity() {
  let observer: MutationObserver | null = null;
  let root: ReturnType<typeof createRoot> | null = null;
  const start = () => {
    const layout = document.querySelector<HTMLElement>('.layout');
    if (!layout || root) return;
    const mount = document.createElement('div');
    mount.className = 'space-continuity-mount';
    layout.appendChild(mount);
    root = createRoot(mount);
    root.render(<ContinuityRail snapshot={demoGateway.snapshotSync()} />);
    observer = new MutationObserver(() => {
      const shell = document.querySelector<HTMLElement>('.shell');
      const current = document.querySelector('.nav-item.active')?.textContent?.trim() as Space | undefined;
      if (shell && current) shell.dataset.space = current;
    });
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
  } else start();
  return () => { observer?.disconnect(); root?.unmount(); };
}
