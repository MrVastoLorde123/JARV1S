import { useEffect, useMemo, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type Space = 'CHAT' | 'CONTROL' | 'MIND' | 'CAPABILITIES';

type Props = { space: Space; snapshot: JarvisSnapshot };

function metric(label: string, value: string | number, detail: string) {
  return { label, value: String(value), detail };
}

export function OperationalInstrumentSurface({ space, snapshot }: Props) {
  const project = snapshot.projects.find((item) => item.state === 'ACTIVE') ?? snapshot.projects[0];
  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE') ?? snapshot.models[0];
  const workspace = snapshot.workspaces.find((item) => item.id === project?.workspaceId);

  if (space === 'CHAT') {
    const cards = [
      metric('INPUT', snapshot.currentFocus, 'Current machine context carried into the next request.'),
      metric('ROUTE', activeModel?.name ?? 'STANDBY', 'The intent enters JARVIS before model selection or action.'),
      metric('SCOPE', workspace?.name ?? 'NO WORKSPACE', 'Explicit workspace boundary for work-producing requests.'),
    ];
    return <InstrumentShell space={space} eyebrow="INTENT MEMBRANE" title="Intent enters here." subtitle="CHAT is the intake instrument: language, direction and outcomes enter the machine before JARVIS decides what kind of work they become." cards={cards} mode="intent">
      <div className="instrument-lane">
        <span className="instrument-node input">01 · EXPRESS</span><i />
        <span className="instrument-node route">02 · INTERPRET</span><i />
        <span className="instrument-node scope">03 · BOUND</span><i />
        <span className="instrument-node handoff">04 · HANDOFF</span>
      </div>
      <div className="instrument-note"><b>CHAT DOES NOT EXECUTE.</b><span>It provides intent and context to the machine; downstream authority remains elsewhere.</span></div>
    </InstrumentShell>;
  }

  if (space === 'CONTROL') {
    const cards = [
      metric('MISSION', project?.name ?? 'NO MISSION', project?.currentAction ?? 'No active action.'),
      metric('MODE', snapshot.mode, snapshot.resources.pressure === 'HIGH' ? 'Resource pressure is shaping execution.' : 'Runtime is within current resource policy.'),
      metric('GUARD', snapshot.resources.strategy, 'Execution policy remains between intention and side effects.'),
    ];
    return <InstrumentShell space={space} eyebrow="ACTION CONSOLE" title="The machine acts here." subtitle="CONTROL is the action instrument: selected mission, authority boundaries, model assignment and guarded transitions converge here." cards={cards} mode="control">
      <div className="control-instrument-grid">
        <div><span>SELECTED OBJECT</span><b>{project?.name ?? 'None'}</b><small>{project?.detail ?? 'Awaiting a mission object.'}</small></div>
        <div><span>ACTIVE HAND</span><b>{activeModel?.name ?? 'No active model'}</b><small>{activeModel?.role ?? 'Model assignment unavailable.'}</small></div>
        <div><span>NEXT EFFECT</span><b>{project?.currentAction ?? 'Waiting for direction'}</b><small>Action requires the appropriate authority path before side effects.</small></div>
      </div>
      <div className="instrument-authority"><span>AUTHORITY PATH</span><b>INTENT → VALIDATE → POLICY → AUTHORIZE → EXECUTE</b><small>Control exposes the machine's actionable boundary without pretending observation is authority.</small></div>
    </InstrumentShell>;
  }

  if (space === 'MIND') {
    const contextCount = snapshot.researchTopics.length + snapshot.plans.length + snapshot.projects.length;
    const cards = [
      metric('FOCUS', snapshot.currentFocus, 'Current context carried by the runtime.'),
      metric('CONTEXT NODES', contextCount, 'Projects, research and plans presently available to the environment.'),
      metric('LEARNING', snapshot.selfActivity.filter((item) => item.kind === 'LEARNING').length, 'Recent learning-shaped runtime signals.'),
    ];
    return <InstrumentShell space={space} eyebrow="CONTEXT FIELD" title="The machine carries context here." subtitle="MIND is the internal-context instrument: memory, knowledge, plans, experiences and relationships give future actions somewhere to come from." cards={cards} mode="mind">
      <div className="mind-instrument-map">
        <div className="mind-orbit core"><span>ACTIVE CONTEXT</span><b>{snapshot.currentFocus}</b></div>
        <div className="mind-orbit memory"><span>MEMORY</span><b>durable context</b></div>
        <div className="mind-orbit learning"><span>LEARNING</span><b>evaluation → adaptation</b></div>
        <div className="mind-orbit plans"><span>PLANS</span><b>{snapshot.plans.length} plan roots</b></div>
        <div className="mind-orbit work"><span>WORK</span><b>{snapshot.projects.length} objects</b></div>
      </div>
      <div className="instrument-note"><b>MIND IS NOT CHAT HISTORY.</b><span>It is the structured context layer that can be consulted by reasoning and action without becoming authority by itself.</span></div>
    </InstrumentShell>;
  }

  const readyCount = snapshot.capabilities.filter((capability) => capability.state === 'READY' || capability.state === 'CONNECTED' || capability.state === 'AVAILABLE' || capability.state === 'ONLINE').length;
  const cards = [
    metric('AVAILABLE', readyCount, `${snapshot.capabilities.length} known capability records are represented.`),
    metric('MODELS', snapshot.models.length, 'Model engines sit inside the wider capability fabric.'),
    metric('ACTIVE', snapshot.activeCapabilities, 'Capabilities currently exposed by the runtime contract.'),
  ];
  return <InstrumentShell space={space} eyebrow="ABILITY FABRIC" title="The machine's abilities live here." subtitle="CAPABILITIES is the ability instrument: models, integrations, workers, devices, plugins and skills become inspectable, scoped and eventually invokable resources." cards={cards} mode="capabilities">
    <div className="capability-instrument-grid">
      {snapshot.capabilities.slice(0, 6).map((capability) => <div className="capability-instrument-card" key={capability.id}><div><span className={`instrument-status ${capability.state.toLowerCase()}`} /><b>{capability.name}</b></div><span>{capability.state}</span><p>{capability.detail}</p></div>)}
    </div>
    <div className="ability-boundary"><span>ABILITY LIFECYCLE</span><b>DISCOVER → INSPECT → TEST → SCOPE → INVOKE → VERIFY</b><small>Capability presence never implies permission to execute.</small></div>
  </InstrumentShell>;
}

function InstrumentShell({ space, eyebrow, title, subtitle, cards, mode, children }: { space: Space; eyebrow: string; title: string; subtitle: string; cards: Array<{ label: string; value: string; detail: string }>; mode: string; children: React.ReactNode }) {
  return <section className={`instrument-surface instrument-${mode}`} data-instrument-space={space}>
    <div className="instrument-heading"><div><span>{eyebrow}</span><h2>{title}</h2><p>{subtitle}</p></div><div className="instrument-identity"><span>{space}</span><b>{mode.toUpperCase()}</b></div></div>
    <div className="instrument-metrics">{cards.map((card) => <div className="instrument-metric" key={card.label}><span>{card.label}</span><b>{card.value}</b><small>{card.detail}</small></div>)}</div>
    <div className="instrument-body">{children}</div>
  </section>;
}

export function OperationalInstrumentController() {
  const [space, setSpace] = useState<Space | null>(null);
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());

  useEffect(() => {
    const unsub = demoGateway.subscribe('operational-instruments', () => setSnapshot(demoGateway.snapshotSync()));
    return unsub;
  }, []);

  useEffect(() => {
    const sync = () => {
      const current = document.querySelector('.nav-item.active')?.textContent?.trim() as Space | undefined;
      setSpace(current && ['CHAT', 'CONTROL', 'MIND', 'CAPABILITIES'].includes(current) ? current : null);
    };
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const targets: Record<Space, string> = {
      CHAT: '.chat-shell',
      CONTROL: '.mission-control',
      MIND: '.mind-core-panel',
      CAPABILITIES: '.capability-grid',
    };
    const targetSelector = space ? targets[space] : null;
    if (!targetSelector) return;
    const target = document.querySelector<HTMLElement>(targetSelector);
    const hostContainer = space === 'CAPABILITIES' ? target?.closest('.space-panel') : target;
    if (!hostContainer) return;

    let host = hostContainer.querySelector<HTMLElement>(':scope > .operational-instrument-mount');
    if (!host) {
      host = document.createElement('div');
      host.className = 'operational-instrument-mount';
      hostContainer.insertBefore(host, hostContainer.firstChild);
    }
    const mount = host;
    const root = document.createElement('div');
    mount.replaceChildren(root);
    const reactRoot = (window as Window & { ReactDOM?: { createRoot?: (element: Element) => { render: (node: React.ReactNode) => void; unmount: () => void } } }).ReactDOM;
    void reactRoot;
  }, [space]);

  return null;
}
