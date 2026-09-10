import { createRoot } from 'react-dom/client';
import React, { useEffect, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type InstrumentSpace = 'CHAT' | 'CONTROL' | 'MIND' | 'CAPABILITIES';
type NodeState = 'CLEAR' | 'ACTIVE' | 'WAITING' | 'BLOCKED' | 'ATTENTION';
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

function stateOf(snapshot: JarvisSnapshot) {
  if (!snapshot.online) return 'OFFLINE';
  if (snapshot.attentionRequired) return 'ATTENTION';
  if (snapshot.resources.pressure === 'HIGH') return 'GUARDED';
  if (snapshot.mode === 'Waiting') return 'WAITING';
  return snapshot.mode.toUpperCase();
}

function nodeStates(snapshot: JarvisSnapshot): Record<InstrumentSpace, NodeState> {
  const modelGap = snapshot.models.every((model) => model.state === 'OFFLINE');
  const waiting = snapshot.mode === 'Waiting' || snapshot.projects.every((project) => project.state !== 'ACTIVE');
  const active = snapshot.mode === 'Working' || snapshot.mode === 'Thinking' || snapshot.mode === 'Learning';
  const pressure = snapshot.resources.pressure === 'HIGH';
  const attention = snapshot.attentionRequired;
  return {
    CHAT: attention ? 'ATTENTION' : active ? 'ACTIVE' : 'CLEAR',
    CONTROL: attention ? 'ATTENTION' : pressure ? 'BLOCKED' : waiting ? 'WAITING' : active ? 'ACTIVE' : 'CLEAR',
    MIND: attention ? 'ATTENTION' : active ? 'ACTIVE' : waiting ? 'WAITING' : 'CLEAR',
    CAPABILITIES: modelGap ? 'BLOCKED' : pressure ? 'WAITING' : snapshot.activeCapabilities > 0 ? 'ACTIVE' : 'CLEAR',
  };
}

function nodeReason(space: InstrumentSpace, nodeState: NodeState, snapshot: JarvisSnapshot) {
  if (nodeState === 'ATTENTION') return snapshot.attentionReason;
  if (nodeState === 'BLOCKED' && space === 'CONTROL') return 'Execution is held behind the resource guard.';
  if (nodeState === 'BLOCKED' && space === 'CAPABILITIES') return 'No healthy model lane is available for invocation.';
  if (nodeState === 'WAITING') return space === 'CONTROL' ? 'The machine is holding for the next actionable transition.' : 'The operation is carrying context while execution waits.';
  if (nodeState === 'ACTIVE') return 'The current operation has live runtime activity here.';
  return 'No elevated state is currently routed to this instrument.';
}

function recordTransition(next: InstrumentSpace) {
  const current = readSpace('jarvis.operation.thread.current');
  if (current && current !== next) sessionStorage.setItem('jarvis.operation.thread.previous', current);
  sessionStorage.setItem('jarvis.operation.thread.current', next);
  sessionStorage.setItem('jarvis.operation.thread.transition', `${current && current !== next ? current : next}->${next}`);
}

function CausalThread({ snapshot }: { snapshot: JarvisSnapshot }) {
  const [space, setSpace] = useState<InstrumentSpace>(() => activeSpace() ?? 'CHAT');
  const [previous, setPrevious] = useState<InstrumentSpace | null>(() => readSpace('jarvis.operation.thread.previous'));
  const [transition, setTransition] = useState(() => sessionStorage.getItem('jarvis.operation.thread.transition') ?? '');

  useEffect(() => {
    const sync = () => {
      const next = activeSpace();
      if (!next) return;
      const current = readSpace('jarvis.operation.thread.current');
      if (current && current !== next) {
        sessionStorage.setItem('jarvis.operation.thread.previous', current);
        sessionStorage.setItem('jarvis.operation.thread.transition', `${current}->${next}`);
        setPrevious(current);
        setTransition(`${current}->${next}`);
      }
      sessionStorage.setItem('jarvis.operation.thread.current', next);
      setSpace(next);
    };
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  const project = snapshot.projects.find((item) => item.state === 'ACTIVE') ?? snapshot.projects.find((item) => item.state === 'WAITING') ?? snapshot.projects[0];
  const workspace = snapshot.workspaces.find((item) => item.id === project?.workspaceId);
  const model = snapshot.models.find((item) => item.state === 'ACTIVE') ?? snapshot.models.find((item) => item.state !== 'OFFLINE') ?? snapshot.models[0];
  const nodes = nodeStates(snapshot);
  const operationState = stateOf(snapshot);
  const currentIndex = spaces.indexOf(space);
  const focus = nodes[space];
  const reason = nodeReason(space, focus, snapshot);

  return <aside className={`causal-thread causal-${space.toLowerCase()} causal-state-${focus.toLowerCase()}`} aria-label="Current operation causal thread">
    <div className="causal-thread-head"><div><span>OPERATION THREAD</span><b>{project?.name ?? snapshot.currentFocus}</b></div><div className="causal-thread-state"><span>{operationState}</span><b>{labels[space]}</b></div></div>
    <div className="causal-path" aria-label="Operation stages">
      {spaces.map((item, index) => <React.Fragment key={item}><div className={`causal-node causal-node-${nodes[item].toLowerCase()} ${index < currentIndex ? 'reached' : ''} ${index === currentIndex ? 'current' : ''}`}><span className="causal-node-label">{labels[item]}</span><small>{nodes[item]}</small></div>{index < spaces.length - 1 && <i className={index < currentIndex ? 'reached' : ''} />}</React.Fragment>)}
    </div>
    <div className="causal-explanation"><div><span>ACTIVE POINT</span><b>{labels[space]} · {focus}</b><small>{reason}</small></div><div><span>HAND-OFF</span><b>{previous && previous !== space ? `${labels[previous]} → ${labels[space]}` : transition || `${labels[space]} established`}</b><small>Same operation. Different instrument. State follows the hand-off.</small></div><div><span>OBJECT</span><b>{workspace?.name ?? 'UNBOUND'} · {model?.name ?? 'STANDBY'}</b><small>{project?.currentAction ?? snapshot.currentFocus}</small></div></div>
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
    recordTransition(current);
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
