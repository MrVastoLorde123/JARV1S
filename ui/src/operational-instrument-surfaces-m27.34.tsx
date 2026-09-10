import { createRoot } from 'react-dom/client';
import React from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

type Space = 'CHAT' | 'CONTROL' | 'MIND' | 'CAPABILITIES';
type RuntimeSignal = 'CLEAR' | 'ATTENTION' | 'PRESSURE' | 'WAITING' | 'ACTIVE' | 'MODEL-GAP' | 'CONTEXT-RICH';
type Density = 'compact' | 'focused' | 'expanded' | 'deferred';
type InstrumentAction = { label: string; detail: string; target: 'CHAT' | 'CONTROL' | 'MIND' | 'CAPABILITIES' | 'SELF' | 'WORK' };

function metric(label: string, value: string | number, detail: string) { return { label, value: String(value), detail }; }

function deriveSignals(snapshot: JarvisSnapshot) {
  const activeModels = snapshot.models.filter((model) => model.state === 'ACTIVE').length;
  const availableModels = snapshot.models.filter((model) => model.state !== 'OFFLINE').length;
  const activeWork = snapshot.projects.filter((project) => project.state === 'ACTIVE').length;
  const waitingWork = snapshot.projects.filter((project) => project.state === 'WAITING').length;
  const contextDepth = snapshot.projects.length + snapshot.researchTopics.length + snapshot.plans.length + snapshot.selfActivity.length;
  const pressure = snapshot.resources.pressure;
  const attention = snapshot.attentionRequired;
  const waiting = snapshot.mode === 'Waiting' || (activeWork === 0 && waitingWork > 0);
  const activity = snapshot.mode === 'Working' || snapshot.mode === 'Thinking' || snapshot.mode === 'Learning';
  const modelGap = activeModels === 0 || availableModels === 0;
  return { activeModels, availableModels, activeWork, waitingWork, contextDepth, pressure, attention, waiting, activity, modelGap };
}

function openSpace(space: InstrumentAction['target']) {
  const button = Array.from(document.querySelectorAll<HTMLButtonElement>('.nav-item')).find((item) => item.textContent?.trim() === space);
  button?.click();
}

function deriveAction(space: Space, signals: ReturnType<typeof deriveSignals>, snapshot: JarvisSnapshot): InstrumentAction {
  if (space === 'CHAT') {
    if (signals.attention) return { label: 'Review attention', detail: 'Open the decision surface before sending more intent.', target: 'CONTROL' };
    if (signals.modelGap) return { label: 'Inspect runtime', detail: 'No healthy model lane is available for immediate routing.', target: 'SELF' };
    if (signals.waiting) return { label: 'Inspect held work', detail: 'The machine is ready to receive direction while execution remains waiting.', target: 'WORK' };
    return { label: 'Give direction', detail: 'Continue into the machine through the existing conversation surface.', target: 'CHAT' };
  }
  if (space === 'CONTROL') {
    if (signals.attention) return { label: 'Resolve attention', detail: snapshot.attentionReason, target: 'CONTROL' };
    if (signals.modelGap) return { label: 'Inspect runtime', detail: 'Resolve the model availability gap before dispatch.', target: 'SELF' };
    if (signals.waiting) return { label: 'Inspect held work', detail: 'Review the waiting mission rather than inventing an action.', target: 'WORK' };
    return { label: 'Inspect context', detail: 'Open the context field behind the current mission.', target: 'MIND' };
  }
  if (space === 'MIND') {
    if (signals.contextDepth >= 16) return { label: 'Inspect orchestration', detail: 'Context is dense enough to review how it is feeding active work.', target: 'CONTROL' };
    if (signals.waiting) return { label: 'Inspect held work', detail: 'Context currently points toward waiting work.', target: 'WORK' };
    return { label: 'Trace active work', detail: 'Open the control surface connected to current context.', target: 'CONTROL' };
  }
  if (signals.modelGap) return { label: 'Inspect runtime', detail: 'The ability fabric is visible, but model availability is blocking invocation.', target: 'SELF' };
  if (signals.pressure === 'HIGH') return { label: 'Inspect runtime guard', detail: 'Resource pressure is shaping what can safely be invoked.', target: 'SELF' };
  return { label: 'Open control', detail: 'Move from available ability into the guarded action surface.', target: 'CONTROL' };
}

function deriveDensity(space: Space, signals: ReturnType<typeof deriveSignals>): Density {
  if (signals.attention) return 'expanded';
  if (signals.modelGap) return space === 'CAPABILITIES' || space === 'CONTROL' ? 'expanded' : 'focused';
  if (signals.pressure === 'HIGH') return space === 'CONTROL' || space === 'CAPABILITIES' ? 'focused' : 'deferred';
  if (signals.waiting) return space === 'CHAT' || space === 'CONTROL' ? 'focused' : 'compact';
  if (space === 'MIND') return signals.contextDepth >= 16 ? 'expanded' : signals.contextDepth >= 8 ? 'focused' : 'compact';
  if (signals.activity) return 'focused';
  return 'compact';
}

export function OperationalInstrumentSurface({ space, snapshot }: { space: Space; snapshot: JarvisSnapshot }) {
  const signals = deriveSignals(snapshot);
  const project = snapshot.projects.find((item) => item.state === 'ACTIVE') ?? snapshot.projects.find((item) => item.state === 'WAITING') ?? snapshot.projects[0];
  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE') ?? snapshot.models.find((model) => model.state !== 'OFFLINE') ?? snapshot.models[0];
  const workspace = snapshot.workspaces.find((item) => item.id === project?.workspaceId);
  const signal = (signals.attention ? 'ATTENTION' : signals.pressure === 'HIGH' ? 'PRESSURE' : signals.waiting ? 'WAITING' : signals.modelGap ? 'MODEL-GAP' : signals.contextDepth >= 16 ? 'CONTEXT-RICH' : signals.activity ? 'ACTIVE' : 'CLEAR') as RuntimeSignal;
  const stateLabel = signals.attention ? 'USER ATTENTION' : signals.pressure === 'HIGH' ? 'HIGH RESOURCE PRESSURE' : signals.waiting ? 'STANDING BY' : signals.modelGap ? 'MODEL AVAILABILITY GAP' : signals.activity ? snapshot.mode.toUpperCase() : 'READY';
  const action = deriveAction(space, signals, snapshot);
  const density = deriveDensity(space, signals);

  if (space === 'CHAT') {
    const cards = [metric('INPUT', snapshot.currentFocus, 'Current machine context carried into the next request.'), metric('ROUTE', activeModel?.name ?? 'STANDBY', signals.modelGap ? 'No healthy active model is available for immediate routing.' : 'Intent enters JARVIS before model selection or action.'), metric('SCOPE', workspace?.name ?? 'NO WORKSPACE', signals.waiting ? 'Requests can enter while execution remains waiting.' : 'Explicit workspace boundary for work-producing requests.')];
    return <InstrumentShell space={space} eyebrow="INTENT MEMBRANE" title="Intent enters here." subtitle="CHAT is the intake instrument: language, direction and outcomes enter the machine before JARVIS decides what kind of work they become." cards={cards} mode="intent" signal={signal} stateLabel={stateLabel} signals={signals} action={action} density={density}>
      {signals.attention && <div className="instrument-alert attention"><b>JARVIS NEEDS YOU.</b><span>{snapshot.attentionReason}</span></div>}
      <div className="instrument-lane"><span className="instrument-node input">01 · EXPRESS</span><i /><span className="instrument-node route">02 · INTERPRET</span><i /><span className="instrument-node scope">03 · BOUND</span><i /><span className="instrument-node handoff">04 · HANDOFF</span></div>
      <div className="instrument-state-grid"><div className="instrument-state-block"><span>INTAKE STATE</span><b>{signals.waiting ? 'QUEUE READY' : 'RECEIVING'}</b><small>{signals.pressure === 'HIGH' ? 'Resource pressure may delay downstream handling.' : 'Natural language can enter the machine normally.'}</small></div><div className="instrument-state-block"><span>MODEL GATE</span><b>{signals.modelGap ? 'HELD' : `${signals.activeModels} ACTIVE`}</b><small>{signals.modelGap ? 'Routing remains visible without pretending execution is available.' : 'A healthy model lane is available.'}</small></div></div>
      {density === 'expanded' && <div className="instrument-reveal"><span>WHY THE INSTRUMENT OPENED UP</span><b>{signals.attention ? 'Your attention outranks passive intake.' : 'The machine needs more visible routing context.'}</b><small>Additional state is exposed instead of forcing the operator to infer why the normal intake path changed.</small></div>}
      <div className="instrument-note"><b>CHAT DOES NOT EXECUTE.</b><span>It provides intent and context to the machine; downstream authority remains elsewhere.</span></div>
    </InstrumentShell>;
  }

  if (space === 'CONTROL') {
    const cards = [metric('MISSION', project?.name ?? 'NO MISSION', project?.currentAction ?? 'No active action.'), metric('MODE', snapshot.mode, signals.pressure === 'HIGH' ? 'Resource pressure is shaping execution.' : signals.waiting ? 'The machine is waiting for an actionable transition.' : 'Runtime is within current resource policy.'), metric('GUARD', snapshot.resources.strategy, 'Execution policy remains between intention and side effects.')];
    return <InstrumentShell space={space} eyebrow="ACTION CONSOLE" title="The machine acts here." subtitle="CONTROL is the action instrument: selected mission, authority boundaries, model assignment and guarded transitions converge here." cards={cards} mode="control" signal={signal} stateLabel={stateLabel} signals={signals} action={action} density={density}>
      <div className="control-instrument-grid"><div className={signals.activeWork ? 'state-active' : 'state-quiet'}><span>SELECTED OBJECT</span><b>{project?.name ?? 'None'}</b><small>{project?.detail ?? 'Awaiting a mission object.'}</small></div><div className={signals.modelGap ? 'state-blocked' : 'state-active'}><span>ACTIVE HAND</span><b>{activeModel?.name ?? 'No active model'}</b><small>{signals.modelGap ? 'No healthy model is ready to take the next execution handoff.' : activeModel?.role ?? 'Model assignment available.'}</small></div><div className={signals.pressure === 'HIGH' || signals.waiting ? 'state-guarded' : 'state-active'}><span>NEXT EFFECT</span><b>{signals.waiting ? 'WAIT FOR TRANSITION' : project?.currentAction ?? 'Waiting for direction'}</b><small>{signals.pressure === 'HIGH' ? 'High pressure keeps the next effect behind the resource guard.' : 'Action requires the appropriate authority path before side effects.'}</small></div></div>
      <div className="instrument-authority"><span>AUTHORITY PATH</span><b>INTENT → VALIDATE → POLICY → AUTHORIZE → EXECUTE</b><small>{signals.attention ? 'User attention is currently part of the control boundary.' : signals.waiting ? 'The machine is holding rather than inventing an action.' : 'Control exposes the machine\'s actionable boundary without pretending observation is authority.'}</small></div>
      {density !== 'compact' && <div className="control-state-banner"><span>{signals.activity ? 'EXECUTION SURFACE' : 'TRANSITION SURFACE'}</span><b>{signals.modelGap ? 'DISPATCH BLOCKED' : signals.waiting ? 'STANDBY GATE' : signals.pressure === 'HIGH' ? 'GUARDED EXECUTION' : 'READY FOR AUTHORIZED ACTION'}</b></div>}
      {density === 'expanded' && <div className="instrument-reveal"><span>CONTROL EXPANSION</span><b>EXPOSE THE TRANSITION, NOT PRIVATE REASONING</b><small>Additional operational detail appears when attention or model availability makes the boundary important to the operator.</small></div>}
    </InstrumentShell>;
  }

  if (space === 'MIND') {
    const learningSignals = snapshot.mode === 'Learning' ? 1 : 0;
    const cards = [metric('FOCUS', snapshot.currentFocus, 'Current context carried by the runtime.'), metric('CONTEXT DEPTH', signals.contextDepth, `${snapshot.projects.length} work + ${snapshot.researchTopics.length} research + ${snapshot.plans.length} plans + ${snapshot.selfActivity.length} recent runtime signals.`), metric('LEARNING', learningSignals, 'Learning-shaped runtime state represented by the current snapshot.')];
    const contextClass = signals.contextDepth >= 16 ? 'rich' : signals.contextDepth >= 8 ? 'layered' : 'sparse';
    return <InstrumentShell space={space} eyebrow="CONTEXT FIELD" title="The machine carries context here." subtitle="MIND is the internal-context instrument: memory, knowledge, plans, experiences and relationships give future actions somewhere to come from." cards={cards} mode="mind" signal={signals.contextDepth >= 16 ? 'CONTEXT-RICH' : signal} stateLabel={signals.contextDepth >= 16 ? 'CONTEXT RICH' : stateLabel} signals={signals} action={action} density={density}>
      <div className={`mind-instrument-map ${contextClass}`}><div className="mind-orbit core"><span>ACTIVE CONTEXT</span><b>{snapshot.currentFocus}</b></div><div className="mind-orbit memory"><span>MEMORY</span><b>{signals.contextDepth >= 8 ? 'durable context present' : 'awaiting depth'}</b></div><div className="mind-orbit learning"><span>LEARNING</span><b>{signals.activity ? 'live signal' : 'evaluation → adaptation'}</b></div><div className="mind-orbit plans"><span>PLANS</span><b>{snapshot.plans.length} plan roots</b></div><div className="mind-orbit work"><span>WORK</span><b>{snapshot.projects.length} objects</b></div></div>
      {density !== 'compact' && <div className="mind-context-strip"><div><span>CONTEXT STATE</span><b>{contextClass.toUpperCase()}</b><small>{contextClass === 'rich' ? 'The field has enough connected material to expose more context density.' : contextClass === 'layered' ? 'Multiple context families are currently available.' : 'The field remains intentionally sparse rather than inventing context.'}</small></div><div><span>MEMORY / LEARNING</span><b>{learningSignals} LEARNING SIGNALS</b><small>Learning signals enrich context but do not become truth by themselves.</small></div></div>}
      <div className="instrument-note"><b>MIND IS NOT CHAT HISTORY.</b><span>It is the structured context layer that can be consulted by reasoning and action without becoming authority by itself.</span></div>
    </InstrumentShell>;
  }

  const readyCount = snapshot.capabilities.filter((capability) => ['READY', 'CONNECTED', 'AVAILABLE', 'ONLINE'].includes(capability.state)).length;
  const unavailableCount = snapshot.capabilities.filter((capability) => ['OFFLINE', 'BLOCKED', 'UNAVAILABLE'].includes(capability.state)).length;
  const cards = [metric('AVAILABLE', readyCount, unavailableCount ? `${unavailableCount} capability records are currently unavailable.` : `${snapshot.capabilities.length} capability records are currently represented.`), metric('MODELS', snapshot.models.length, signals.modelGap ? 'Model availability is currently limiting the usable ability fabric.' : `${signals.activeModels} active model lane${signals.activeModels === 1 ? '' : 's'} currently available.`), metric('ACTIVE', snapshot.activeCapabilities, signals.pressure === 'HIGH' ? 'Active capability use is subject to elevated resource pressure.' : 'Capabilities currently exposed by the runtime contract.')];
  return <InstrumentShell space={space} eyebrow="ABILITY FABRIC" title="The machine's abilities live here." subtitle="CAPABILITIES is the ability instrument: models, integrations, workers, devices, plugins and skills become inspectable, scoped and eventually invokable resources." cards={cards} mode="capabilities" signal={signals.modelGap ? 'MODEL-GAP' : signal} stateLabel={signals.modelGap ? 'MODEL AVAILABILITY GAP' : stateLabel} signals={signals} action={action} density={density}>
    <div className="capability-instrument-grid">{snapshot.capabilities.slice(0, 6).map((capability) => <div className={`capability-instrument-card state-${capability.state.toLowerCase()}`} key={capability.id}><div><span className="instrument-status" /><b>{capability.name}</b></div><span>{capability.state}</span><p>{capability.detail}</p></div>)}</div>
    {density !== 'compact' && <div className="capability-runtime-state"><div><span>INVOCATION STATE</span><b>{signals.modelGap ? 'MODEL GATE CLOSED' : signals.pressure === 'HIGH' ? 'RESOURCE-GUARDED' : 'AVAILABLE TO SCOPE'}</b><small>{signals.modelGap ? 'The ability fabric remains inspectable while invocation waits for a usable model lane.' : 'Presence remains separate from permission; every invocation still follows its authority path.'}</small></div><div><span>RUNTIME PRESSURE</span><b>{snapshot.resources.pressure}</b><small>{signals.pressure === 'HIGH' ? 'High pressure is now visible at the capability boundary.' : 'No elevated capability pressure is being expressed.'}</small></div></div>}
    {density === 'deferred' && <div className="instrument-reveal"><span>DETAIL DEFERRED</span><b>CAPABILITY DETAIL YIELDS TO RUNTIME PRESSURE</b><small>The fabric stays inspectable while secondary operational detail is intentionally quiet.</small></div>}
    <div className="ability-boundary"><span>ABILITY LIFECYCLE</span><b>DISCOVER → INSPECT → TEST → SCOPE → INVOKE → VERIFY</b><small>Capability presence never implies permission to execute.</small></div>
  </InstrumentShell>;
}

function InstrumentShell({ space, eyebrow, title, subtitle, cards, mode, signal, stateLabel, signals, action, density, children }: { space: Space; eyebrow: string; title: string; subtitle: string; cards: Array<{ label: string; value: string; detail: string }>; mode: string; signal: RuntimeSignal; stateLabel: string; signals: ReturnType<typeof deriveSignals>; action: InstrumentAction; density: Density; children: React.ReactNode }) {
  return <section className={`instrument-surface instrument-${mode} instrument-signal-${signal.toLowerCase()} instrument-pressure-${signals.pressure.toLowerCase()} instrument-density-${density} ${signals.attention ? 'instrument-attention' : ''} ${signals.waiting ? 'instrument-waiting' : ''} ${signals.activity ? 'instrument-active' : ''}`} data-instrument-space={space} data-runtime-signal={signal} data-density={density}>
    <div className="instrument-heading"><div><span>{eyebrow}</span><h2>{title}</h2><p>{subtitle}</p></div><div className="instrument-identity"><span>{space}</span><b>{mode.toUpperCase()}</b></div></div>
    <div className="instrument-statebar"><span className="instrument-signal-dot" /><b>{stateLabel}</b><small>{signals.activeWork} ACTIVE WORK · {signals.activeModels} ACTIVE MODEL{signals.activeModels === 1 ? '' : 'S'} · {signals.pressure} PRESSURE</small></div>
    <div className="instrument-metrics">{cards.map((card) => <div className="instrument-metric" key={card.label}><span>{card.label}</span><b>{card.value}</b><small>{card.detail}</small></div>)}</div>
    <div className="instrument-body">{children}</div>
    <div className="instrument-action"><div><span>NEXT MOVE</span><b>{action.label}</b><small>{action.detail}</small></div><button onClick={() => openSpace(action.target)}>OPEN →</button></div>
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
    if (!next || !selector) { root?.unmount(); mount?.remove(); root = null; mount = null; currentSpace = null; return; }
    const target = document.querySelector<HTMLElement>(selector);
    const container = next === 'CAPABILITIES' ? target?.closest('.space-panel') : target;
    if (!container) return;
    if (!mount || currentSpace !== next || !container.contains(mount)) { root?.unmount(); mount?.remove(); mount = document.createElement('div'); mount.className = 'operational-instrument-mount'; container.insertBefore(mount, container.firstChild); root = createRoot(mount); currentSpace = next; }
    const renderRoot = root;
    if (!renderRoot) return;
    renderRoot.render(<OperationalInstrumentSurface space={next} snapshot={snapshot} />);
  };
  const start = () => {
    sync();
    unsubscribe = demoGateway.subscribe('operational-instrument-surfaces', () => { snapshot = demoGateway.snapshotSync(); sync(); });
    observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true }); else start();
  return () => { unsubscribe?.(); observer?.disconnect(); root?.unmount(); mount?.remove(); };
}