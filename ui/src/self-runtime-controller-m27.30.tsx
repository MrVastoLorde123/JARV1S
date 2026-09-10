import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';
import SelfRuntime from './SelfRuntime';

function openMissionControl() {
  const control = Array.from(document.querySelectorAll<HTMLButtonElement>('.nav-item')).find((item) => item.textContent?.trim() === 'CONTROL');
  control?.click();
}

function RuntimeMount() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());

  useEffect(() => demoGateway.subscribe('self-runtime', () => setSnapshot(demoGateway.snapshotSync())), []);

  return <SelfRuntime snapshot={snapshot} onOpenControl={openMissionControl} />;
}

export function installSelfRuntime() {
  const installed = new WeakSet<HTMLElement>();
  let observer: MutationObserver | null = null;

  const sync = () => {
    const host = Array.from(document.querySelectorAll<HTMLElement>('.space-panel')).find((panel) => panel.querySelector('.self-head'));
    if (!host || installed.has(host)) return;

    const mount = document.createElement('div');
    mount.className = 'self-runtime-mount';
    mount.setAttribute('aria-label', 'JARVIS runtime environment');
    host.appendChild(mount);
    host.classList.add('self-runtime-mounted');
    createRoot(mount).render(<RuntimeMount />);
    installed.add(host);
  };

  const start = () => {
    sync();
    observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start, { once: true });
    return () => { observer?.disconnect(); };
  }

  start();
  return () => observer?.disconnect();
}
