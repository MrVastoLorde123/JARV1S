import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type InstrumentSpace = 'CHAT' | 'CONTROL' | 'MIND' | 'CAPABILITIES';
const spaces: InstrumentSpace[] = ['CHAT', 'CONTROL', 'MIND', 'CAPABILITIES'];
const labels: Record<InstrumentSpace, string> = {
  CHAT: 'INTENT',
  CONTROL: 'ACTION',
  MIND: 'CONTEXT',
  CAPABILITIES: 'ABILITY',
};

function activeSpace(): InstrumentSpace | null {
  const value = document.querySelector('.nav-item.active')?.textContent?.trim();
  return spaces.includes(value as InstrumentSpace) ? value as InstrumentSpace : null;
}

function lastSpace(): InstrumentSpace | null {
  const value = sessionStorage.getItem('jarvis.operation.last-instrument');
  return spaces.includes(value as InstrumentSpace) ? value as InstrumentSpace : null;
}

function setSpace(next: InstrumentSpace) {
  const previous = activeSpace();
  if (previous && previous !== next) sessionStorage.setItem('jarvis.operation.last-instrument', previous);
  sessionStorage.setItem('jarvis.operation.instrument', next);
}

function OperationContinuity({ snapshot }: { snapshot: JarvisSnapshot }) {
  const [space, setSpaceState] = useState<InstrumentSpace>(() => activeSpace() ?? 'CHAT');
  const [previous, setPrevious] = useState<InstrumentSpace | null>(() => lastSpace());

  useEffect(() => {
    const sync = () => {
      const next = activeSpace();
      if (!next) return;
      const prior = lastSpace();
      if (prior !== next) setPrevious(prior);
      setSpace(next);
      setSpaceState(next);
    };
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const project = snapshot.projects.find((item) => item.state === 'ACTIVE') ?? snapshot.projects.find((item) => item.state === 'WAITING') ?? snapshot.projects[0];
  const workspace = snapshot.workspaces.find((item) => item.id === project?.workspaceId);
  const model = snapshot.models.find((item) => item.state === 'ACTIVE') ?? snapshot.models.find((item) => item.state !== 'OFFLINE') ?? snapshot.models[0];
  const state = snapshot.attentionRequired ? 'ATTENTION' : snapshot.resources.pressure === 'HIGH' ? 'GUARDED' : snapshot.mode.toUpperCase();

  return <div className={`operation-continuity operation-${space.toLowerCase()} operation-state-${state.toLowerCase()}`} data-operation-space={space}>
    <div className="operation-trace"><span className="operation-kicker">CURRENT OPERATION</span><b>{project?.name ?? snapshot.currentFocus}</b><span className="operation-state">{state}</span></div>
    <div className="operation-chain">
      <div className="operation-object"><span>WORKSPACE</span><b>{workspace?.name ?? 'UNBOUND'}</b></div>
      <div className="operation-object"><span>MODEL</span><b>{model?.name ?? 'STANDBY'}</b></div>
      <div className="operation-object"><span>TRANSITION</span><b>{project?.currentAction ?? snapshot.currentFocus}</b></div>
      <div className="operation-route"><span>{previous ? `${labels[previous]} → ` : ''}{labels[space]}</span><small>{previous ? 'same operation · new instrument' : 'operation established'}</small></div>
    </div>
  </div>;
}

export function installOperationContinuity() {
  let root: ReturnType<typeof createRoot> | null = null;
  let mount: HTMLDivElement | null = null;
  let observer: MutationObserver | null = null;
  let unsubscribe: (() => void) | null = null;
  let currentSpace: InstrumentSpace | null = null;
  let snapshot = demoGateway.snapshotSync();

  const sync = () => {
    const current = activeSpace();
    const instrumentMount = document.querySelector<HTMLElement>('.operational-instrument-mount');
    if (!current || !instrumentMount?.parentElement) {
      root?.unmount(); mount?.remove(); root = null; mount = null; currentSpace = null; return;
    }
    if (!mount || currentSpace !== current || !instrumentMount.parentElement.contains(mount)) {
      root?.unmount(); mount?.remove(); mount = document.createElement('div'); mount.className = 'operation-continuity-mount';
      instrumentMount.parentElement.insertBefore(mount, instrumentMount);
      root = createRoot(mount); currentSpace = current;
    }
    setSpace(current);
    root.render(<OperationContinuity snapshot={snapshot} />);
  };

  const start = () => {
    sync();
    unsubscribe = demoGateway.subscribe('operation-continuity', () => { snapshot = demoGateway.snapshotSync(); sync(); });
    observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
  return () => { unsubscribe?.(); observer?.disconnect(); root?.unmount(); mount?.remove(); };
}
