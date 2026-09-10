import { createRoot } from 'react-dom/client';
import type { ReactNode } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type Space = 'CHAT' | 'CONTROL' | 'MIND' | 'CAPABILITIES';

function metric(label: string, value: string | number, detail: string) {
  return { label, value: String(value), detail };
}

export function OperationalInstrumentSurface({ space, snapshot }: { space: Space; snapshot: JarvisSnapshot }) {
  const project = snapshot.projects.find((item) => item.state === 'ACTIVE') ?? snapshot.projects[0];
  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE') ?? snapshot.models[0];
  const workspace = snapshot.workspaces.find((item) => item.id === project?.workspaceId);

  if (space === 'CHAT') {
    const cards = [
      metric('INPUT', snapshot.currentFocus, 'Current machine context carried into the next request.'),
      metric('ROUTE', activeModel?.name ?? 'STANDBY', 'Intent enters JARVIS before model selection or action.'),
      metric('SCOPE', workspace?.name ?? 'NO WORKSPACE', 'Explicit workspace boundary for work-producing requests.'),
    ];
    return <InstrumentShell space={space} eyebrow="INTENT MEMBRANE" title="Intent enters here." subtitle="CHAT is the intake instrument: language, direction and outcomes enter the machine before JARVIS decides what kind of work they become." cards={cards} mode="intent">
      <div className="instrument-lane"><span className="instrument-node input">01 · EXPRESS</span><i /><span className="instrument-node route">02 · INTERPRET</span><i /><span className="instrument-node scope">03 · BOUND</span><i /><span className="instrument-node handoff">04 · HANDOFF</span></div>
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
      <div className="control-instrument-grid"><div><span>SELECTED OBJECT</span><b>{project?.name ?? 'None'}</b><small>{project?.detail ?? 'Awaiting a mission object.'}</small></div><div><span>ACTIVE HAND</span><b>{activeModel?.name ?? 'No active model'}</b><small>{activeModel?.role ?? 'Model assignment unavailable.'}</small></div><div><span>NEXT EFFECT</span><b>{project?.currentAction ?? 'Waiting for direction'}</b><small>Action requires the appropriate authority path before side effects.</small></div></div>
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
      <div className="mind-instrument-map"><div className="mind-orbit core"><span>ACTIVE CONTEXT</span><b>{snapshot.currentFocus}</b></div><div className="mind-orbit memory"><span>MEMORY</span><b>durable context</b></div><div className="mind-orbit learning"><span>LEARNING</span><b>evaluation → adaptation</b></div><div className="mind-orbit plans"><span>PLANS</span><b>{snapshot.plans.length} plan roots</b></div><div className="mind-orbit work"><span>WORK</span><b>{snapshot.projects.length} objects</b></div></div>
      <div className="instrument-note"><b>MIND IS NOT CHAT HISTORY.</b><span>It is the structured context layer that can be consulted by reasoning and action without becoming authority by itself.</span></div>
    </InstrumentShell>;
  }

  const readyCount = snapshot.capabilities.filter((capability) => ['READY', 'CONNECTED', 'AVAILABLE', 'ONLINE'].includes(capability.state)).length;
  const cards = [
    metric('AVAILABLE', readyCount, `${snapshot.capabilities.length} known capability records are represented.`),
    metric('MODELS', snapshot.models.length, 'Model engines sit inside the wider capability fabric.'),
    metric('ACTIVE', snapshot.activeCapabilities, 'Capabilities currently exposed by the runtime contract.'),
  ];
  return <InstrumentShell space={space} eyebrow="ABILITY FABRIC" title="The machine's abilities live here." subtitle="CAPABILITIES is the ability instrument: models, integrations, workers, devices, plugins and skills become inspectable, scoped and eventually invokable resources." cards={cards} mode="capabilities">
    <div className="capability-instrument-grid">{snapshot.capabilities.slice(0, 6).map((capability) => <div className="capability-instrument-card" key={capability.id}><div><span className={`instrument-status ${capability.state.toLowerCase()}`} /><b>{capability.name}</b></div><span>{capability.state}</span><p>{capability.detail}</p></div>)}</div>
    <div className="ability-boundary"><span>ABILITY LIFECYCLE</span><b>DISCOVER → INSPECT → TEST → SCOPE → INVOKE → VERIFY</b><small>Capability presence never implies permission to execute.</small></div>
  </InstrumentShell>;
}

function InstrumentShell({ space, eyebrow, title, subtitle, cards, mode, children }: { space: Space; eyebrow: string; title: string; subtitle: string; cards: Array<{ label: string; value: string; detail: string }>; mode: string; children: ReactNode }) {
  return <section className={`instrument-surface instrument-${mode}`} data-instrument-space={space}>
    <div className="instrument-heading"><div><span>{eyebrow}</span><h2>{title}</h2><p>{subtitle}</p></div><div className="instrument-identity"><span>{space}</span><b>{mode.toUpperCase()}</b></div></div>
    <div className="instrument-metrics">{cards.map((card) => <div className="instrument-metric" key={card.label}><span>{card.label}</span><b>{card.value}</b><small>{card.detail}</small></div>)}</div>
    <div className="instrument-body">{children}</div>
  </section>;
}

export function installOperationalInstrumentSurfaces() {
  let root: ReturnType<typeof createRoot> | null = null;
  let mount: HTMLDivElement | null = null;
  let observer: MutationObserver | null = null;
  let unsubscribe: (() => void) | null = null;
  let currentSpace: Space | null = null;
  let snapshot = demoGateway.snapshotSync();

  const sync = () => {
    const active = document.querySelector('.nav-item.active')?.textContent?.trim() as Space | undefined;
    const next = active && ['CHAT', 'CONTROL', 'MIND', 'CAPABILITIES'].includes(active) ? active : null;
    const selector = next === 'CHAT' ? '.chat-shell' : next === 'CONTROL' ? '.mission-control' : next === 'MIND' ? '.mind-core-panel' : next === 'CAPABILITIES' ? '.space-panel .capability-grid' : null;
    if (!next || !selector) {
      root?.unmount();
      mount?.remove();
      root = null;
      mount = null;
      currentSpace = null;
      return;
    }

    const target = document.querySelector<HTMLElement>(selector);
    const container = next === 'CAPABILITIES' ? target?.closest('.space-panel') : target;
    const parent = container?.parentElement;
    if (!container || !parent) return;

    if (!mount || currentSpace !== next || mount.parentElement !== parent) {
      root?.unmount();
      mount?.remove();
      mount = document.createElement('div');
      mount.className = 'operational-instrument-mount';
      parent.insertBefore(mount, container);
      root = createRoot(mount);
      currentSpace = next;
    }
    root.render(<OperationalInstrumentSurface space={next} snapshot={snapshot} />);
  };

  const start = () => {
    sync();
    unsubscribe = demoGateway.subscribe('operational-instrument-surfaces', () => { snapshot = demoGateway.snapshotSync(); sync(); });
    observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
  return () => { unsubscribe?.(); observer?.disconnect(); root?.unmount(); mount?.remove(); };
}
