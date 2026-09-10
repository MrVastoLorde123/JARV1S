import type { CSSProperties } from 'react';
import type { JarvisSnapshot } from './contracts';

interface SelfRuntimeProps {
  snapshot: JarvisSnapshot;
  onOpenControl: () => void;
}

function SelfRuntime({ snapshot, onOpenControl }: SelfRuntimeProps) {
  const activeModel = snapshot.models.find((model) => model.state === 'ACTIVE');
  const activeProject = snapshot.projects.find((project) => project.state === 'ACTIVE') ?? snapshot.projects[0];
  const busyModels = snapshot.models.filter((model) => model.state === 'ACTIVE');
  const observed = snapshot.selfActivity.slice(0, 4);
  const pressure = snapshot.resources.pressure;
  const capacity = snapshot.resources.concurrencyLimit;
  const metricStyle = (load: number): CSSProperties => ({ '--load': `${load}%` } as CSSProperties);

  return (
    <div className="self-runtime-live">
      <header className="self-runtime-banner">
        <div>
          <span className="surface-label">RUNTIME ENVIRONMENT</span>
          <strong>{snapshot.online ? 'JARVIS is operational.' : 'JARVIS core is unreachable.'}</strong>
          <p>{snapshot.online ? snapshot.currentFocus : 'The interface is preserving the last known runtime state while core connectivity is unavailable.'}</p>
        </div>
        <div className={`self-runtime-health health-${snapshot.online ? 'online' : 'offline'}`}>
          <span>{snapshot.online ? 'ONLINE' : 'OFFLINE'}</span>
          <small>{snapshot.mode}</small>
        </div>
      </header>

      <section className="self-execution-thread" aria-label="Current execution thread">
        <div className="self-thread-node"><span>MISSION</span><b>{activeProject?.name ?? 'No active work'}</b><small>{activeProject?.state ?? 'IDLE'}</small></div>
        <i aria-hidden="true" />
        <div className="self-thread-node"><span>STAGE</span><b>{snapshot.mode}</b><small>{snapshot.workRuntime.state}</small></div>
        <i aria-hidden="true" />
        <div className="self-thread-node"><span>MODEL</span><b>{activeModel?.name ?? 'No active model'}</b><small>{activeModel?.role ?? 'Standby'}</small></div>
        <i aria-hidden="true" />
        <div className="self-thread-node"><span>RESOURCE</span><b>{pressure}</b><small>{snapshot.resources.activeModelTasks}/{capacity} concurrency</small></div>
      </section>

      <div className="self-runtime-grid">
        <section className="self-runtime-lane self-resource-lane">
          <div className="self-lane-head"><span>RESOURCE FIELD</span><small>{pressure} · {snapshot.resources.strategy}</small></div>
          <div className="self-resource-orbit">
            <div className={`resource-core pressure-${pressure.toLowerCase()}`}><b>{snapshot.resources.activeModelTasks}/{capacity}</b><span>MODEL TASKS</span></div>
            <div className="resource-metric metric-cpu"><span>CPU</span><b>{snapshot.resources.cpuLoad}%</b><i style={metricStyle(snapshot.resources.cpuLoad)} /></div>
            <div className="resource-metric metric-memory"><span>MEM</span><b>{snapshot.resources.memoryLoad}%</b><i style={metricStyle(snapshot.resources.memoryLoad)} /></div>
            <div className="resource-metric metric-gpu"><span>GPU</span><b>{snapshot.resources.gpuLoad}%</b><i style={metricStyle(snapshot.resources.gpuLoad)} /></div>
          </div>
          <p className="self-lane-note">JARVIS adjusts model concurrency from observed resource pressure rather than assuming unlimited parallel work.</p>
        </section>

        <section className="self-runtime-lane self-model-lane">
          <div className="self-lane-head"><span>MODEL FLEET</span><small>{busyModels.length} ACTIVE · {snapshot.models.length} KNOWN</small></div>
          <div className="self-model-stack">
            {snapshot.models.map((model) => (
              <button className={`self-model-node state-${model.state.toLowerCase()}`} key={model.id} onClick={onOpenControl}>
                <span className="self-model-node-mark">{model.state === 'ACTIVE' ? '●' : model.state === 'IDLE' ? '·' : '×'}</span>
                <span className="self-model-node-copy"><b>{model.name}</b><small>{model.role}</small></span>
                <span className="self-model-node-meta">{model.state}</span>
              </button>
            ))}
          </div>
          <div className="self-model-focus"><span>CURRENT LANE</span><b>{activeModel?.name ?? 'NO ACTIVE MODEL'}</b><small>{activeModel?.detail ?? 'Waiting for an operational model.'}</small></div>
        </section>

        <section className="self-runtime-lane self-operation-lane">
          <div className="self-lane-head"><span>CURRENT OPERATION</span><small>{snapshot.workRuntime.state}</small></div>
          <div className="self-operation-stage"><span>FOCUS</span><b>{snapshot.currentFocus}</b><small>{snapshot.workRuntime.detail}</small></div>
          <div className="self-operation-route"><span className="route-node done">CONTEXT</span><i /> <span className={snapshot.mode === 'Thinking' ? 'route-node active' : 'route-node'}>REASON</span><i /> <span className={snapshot.mode === 'Working' ? 'route-node active' : 'route-node'}>ACT</span><i /> <span className={snapshot.mode === 'Learning' ? 'route-node active' : 'route-node'}>VERIFY</span></div>
          <button className="soft-action self-operation-action" onClick={onOpenControl}>Inspect orchestration →</button>
        </section>

        <section className="self-runtime-lane self-observation-lane">
          <div className="self-lane-head"><span>OBSERVATION RAIL</span><small>STRUCTURED · {observed.length}</small></div>
          <div className="self-observation-list">
            {observed.length === 0 ? <div className="self-observation-empty">No structured runtime observations are currently available.</div> : observed.map((item) => (
              <div className="self-observation-item" key={item.id}>
                <span className={`observation-kind kind-${item.kind.toLowerCase()}`} />
                <div><b>{item.title}</b><p>{item.detail}</p></div>
                <time>{item.timestamp}</time>
              </div>
            ))}
          </div>
        </section>
      </div>

      <footer className="self-runtime-foot"><span>OBSERVATION IS NOT AUTHORITY</span><b>{snapshot.online ? 'Runtime state is live from the current snapshot.' : 'Last known state is being preserved.'}</b></footer>
    </div>
  );
}

export default SelfRuntime;
