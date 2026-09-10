import { createRoot } from 'react-dom/client';
import React, { useEffect, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type InstrumentSpace = 'CHAT' | 'CONTROL' | 'MIND' | 'CAPABILITIES';
const spaces: InstrumentSpace[] = ['CHAT', 'CONTROL', 'MIND', 'CAPABILITIES'];
const labels: Record<InstrumentSpace, string> = { CHAT: 'INTENT', CONTROL: 'ACTION', MIND: 'CONTEXT', CAPABILITIES: 'ABILITY' };

function readSpace(key: string): InstrumentSpace | null {
  const value = sessionStorage.getItem(key);
  return spaces.includes(value as InstrumentSpace) ? value as InstrumentSpace : null;
}

function activeSpace(): InstrumentSpace | null {
  const value = document.querySelector('.nav-item.active')?.textContent?.trim();
  return spaces.includes(value as InstrumentSpace) ? value as InstrumentSpace : null;
}

function recordTransition(next: InstrumentSpace) {
  const previous = activeSpace();
  if (!previous || previous === next) return;
  sessionStorage.setItem('jarvis.operation.thread.previous', previous);
  sessionStorage.setItem('jarvis.operation.thread.current', next);
  sessionStorage.setItem('jarvis.operation.thread.transition', `${previous}->${next}`);
}

function stateOf(snapshot: JarvisSnapshot) {
  if (!snapshot.online) return 'OFFLINE';
  if (snapshot.attentionRequired) return 'ATTENTION';
  if (snapshot.resources.pressure === 'HIGH') return 'GUARDED';
  if (snapshot.mode === 'Waiting') return 'WAITING';
  return snapshot.mode.toUpperCase();
}

function CausalThread({ snapshot }: { snapshot: JarvisSnapshot }) {
  const [space, setSpace] = useState<InstrumentSpace>(() => activeSpace() ?? 'CHAT');
  const [previous, setPrevious] = useState<InstrumentSpace | null>(() => readSpace('jarvis.operation.thread.previous'));
  const [transition, setTransition] = useState<string>(() => sessionStorage.getItem('jarvis.operation.thread.transition') ?? '');

  useEffect(() => {
    const sync = () => {
      const next = activeSpace();
      if (!next) return;
      const prior = activeSpace();
      const remembered = readSpace('jarvis.operation.thread.current');
      const from = remembered && remembered !== next ? remembered : readSpace('jarvis.operation.last-instrument');
      if (from && from !== next) {
        sessionStorage.setItem('jarvis.operation.thread.previous', from);
        sessionStorage.setItem('jarvis.operation.thread.current', next);
        sessionStorage.setItem('jarvis.operation.thread.transition', `${from}->${next}`);
        setPrevious(from);
        setTransition(`${from}->${next}`);
      }
      setSpace(next);
      recordTransition(next);
    };
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const project = snapshot.projects.find((item) => item.state === 'ACTIVE') ?? snapshot.projects.find((item) => item.state === 'WAITING') ?? snapshot.projects[0];
  const workspace = snapshot.workspaces.find((item) => item.id === project?.workspaceId);
  const model = snapshot.models.find((item) => item.state === 'ACTIVE') ?? snapshot.models.find((item) => item.state !== 'OFFLINE') ?? snapshot.models[0];
  const state = stateOf(snapshot);
  const currentIndex = spaces.indexOf(space);

  return <aside className={`causal-thread causal-${space.toLowerCase()} causal-state-${state.toLowerCase()}`} aria-label="Current operation causal thread">
    <div className="causal-thread-head"><span>OPERATION THREAD</span><b>{project?.name ?? snapshot.currentFocus}</b><small>{state}</small></div>
    <div className="causal-thread-body">
      <div className="causal-path">
        {spaces.map((item, index) => <React.Fragment key={item}><span className={`causal-node ${index <= currentIndex ? 'reached' : ''} ${item === space ? 'current' : ''}`}>{labels[item]}</span>{index < spaces.length - 1 && <i className={index < currentIndex ? 'reached' : ''} />}</React.Fragment>)}
      </div>
      <div className="causal-handoff"><div><span>HANDOFF</span><b>{previous && previous !== space ? `${labels[previous]} → ${labels[space]}` : transition || `${labels[space]} active`}</b><small>{previous && previous !== space ? 'The operation remains the same while its instrument changes.' : 'This operation is currently established in the active instrument.'}</small></div><div><span>OBJECT</span><b>{workspace?.name ?? 'UNBOUND'} · {model?.name ?? 'STANDBY'}</b><small>{project?.currentAction ?? snapshot.currentFocus}</small></div></div>
    </div>
  </aside>;
}

export function installCausalThread() {
  let root: ReturnType<typeof createRoot> | null = null;
  let mount: HTMLDivElement | null = null;
  let observer: MutationObserver | null = null;
  let unsubscribe: (() => void) | null = null;
  let snapshot = demoGateway.snapshotSync();

  const sync = () => {
    const current = activeSpace();
    const host = document.querySelector<HTMLElement>('.operation-continuity-mount');
    if (!current || !host?.parentElement) { root?.unmount(); mount?.remove(); root = null; mount = null; return; }
    if (!mount || !host.parentElement.contains(mount)) {
      root?.unmount(); mount?.remove(); mount = document.createElement('div'); mount.className = 'causal-thread-mount'; host.parentElement.insertBefore(mount, host.nextSibling); root = createRoot(mount);
    }
    root.render(<CausalThread snapshot={snapshot} />);
  };

  const start = () => {
    sync();
    unsubscribe = demoGateway.subscribe('causal-thread', () => { snapshot = demoGateway.snapshotSync(); sync(); });
    observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
  return () => { unsubscribe?.(); observer?.disconnect(); root?.unmount(); mount?.remove(); };
}
