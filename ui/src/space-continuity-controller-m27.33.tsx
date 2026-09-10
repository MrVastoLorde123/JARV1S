import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type Space = 'HOME' | 'CHAT' | 'WORK' | 'CONTROL' | 'MIND' | 'CAPABILITIES' | 'SELF';

const spaces: Array<{ id: Space; detail: string }> = [
  { id: 'HOME', detail: 'orientation' },
  { id: 'CHAT', detail: 'intent' },
  { id: 'WORK', detail: 'execution' },
  { id: 'CONTROL', detail: 'authority' },
  { id: 'MIND', detail: 'context' },
  { id: 'CAPABILITIES', detail: 'power' },
  { id: 'SELF', detail: 'runtime' },
];

function openSpace(space: Space) {
  const button = Array.from(document.querySelectorAll<HTMLButtonElement>('.nav-item')).find((item) => item.textContent?.trim() === space);
  button?.click();
}

function ContinuityRail({ snapshot }: { snapshot: JarvisSnapshot }) {
  const [active, setActive] = useState<Space>(() => {
    const shell = document.querySelector<HTMLElement>('.shell');
    const current = shell?.dataset.space as Space | undefined;
    return current ?? 'HOME';
  });

  useEffect(() => {
    const sync = () => {
      const shell = document.querySelector<HTMLElement>('.shell');
      const current = shell?.dataset.space as Space | undefined;
      if (current) setActive(current);
    };
    sync();
    const observer = new MutationObserver(sync);
    const shell = document.querySelector<HTMLElement>('.shell');
    if (shell) observer.observe(shell, { attributes: true, attributeFilter: ['data-space'] });
    return () => observer.disconnect();
  }, []);

  const currentIndex = spaces.findIndex((space) => space.id === active);
  const mission = snapshot.projects.find((project) => project.state === 'ACTIVE') ?? snapshot.projects[0];
  return <nav className="space-continuity-rail" aria-label="JARVIS operating instruments">
    {spaces.map((space, index) => (
      <button key={space.id} className={`space-continuity-link ${active === space.id ? 'active' : ''}`} onClick={() => { setActive(space.id); openSpace(space.id); }}>
        <span className="space-continuity-index">{String(index + 1).padStart(2, '0')}</span>
        <span className="space-continuity-copy"><b>{space.id}</b><small>{space.detail}{index === currentIndex ? ` · ${mission?.name ?? snapshot.currentFocus}` : ''}</small></span>
      </button>
    ))}
  </nav>;
}

export function installSpaceContinuity() {
  const installed = new WeakSet<HTMLElement>();
  let observer: MutationObserver | null = null;
  const snapshot = demoGateway.snapshotSync();
  const sync = () => {
    const shell = document.querySelector<HTMLElement>('.shell');
    const layout = document.querySelector<HTMLElement>('.layout');
    if (!shell || !layout || installed.has(layout)) return;
    shell.dataset.space = (document.querySelector('.nav-item.active')?.textContent?.trim() || 'HOME') as Space;
    const mount = document.createElement('div');
    mount.className = 'space-continuity-mount';
    layout.insertBefore(mount, layout.firstChild?.nextSibling ?? layout.firstChild);
    createPortal(<ContinuityRail snapshot={snapshot} />, mount);
    installed.add(layout);
  };
  const start = () => {
    sync();
    observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer?.disconnect();
  };
  if (document.readyState === 'loading') {
    let cleanup: (() => void) | undefined;
    document.addEventListener('DOMContentLoaded', () => { cleanup = start(); }, { once: true });
    return () => cleanup?.();
  }
  return start();
}
