import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot, SelfActivityContract } from './contracts';

function sceneKind(snapshot: JarvisSnapshot) {
  if (!snapshot.online) return 'offline';
  if (snapshot.attentionRequired || snapshot.mode === 'Needs You') return 'decision';
  if (snapshot.mode === 'Working') return 'working';
  if (snapshot.mode === 'Thinking') return 'thinking';
  if (snapshot.mode === 'Learning') return 'learning';
  if (snapshot.mode === 'Monitoring') return 'monitoring';
  return 'quiet';
}

function activityRole(item: SelfActivityContract) {
  if (item.kind === 'THINKING') return 'thought';
  if (item.kind === 'DELEGATING') return 'move';
  if (item.kind === 'COMMUNICATING') return 'signal';
  if (item.kind === 'RESOURCE_GUARD') return 'guard';
  return 'wait';
}

export default function JarvisWorldWorkScene() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());
  const [arrival, setArrival] = useState<string | null>(null);
  const knownActivity = useRef(new Set(snapshot.selfActivity.map((item) => item.id)));

  useEffect(() => demoGateway.subscribe('jarvis-world-scene', () => {
    const next = demoGateway.snapshotSync();
    const newest = next.selfActivity.find((item) => !knownActivity.current.has(item.id));
    if (newest) {
      knownActivity.current = new Set(next.selfActivity.map((item) => item.id));
      setArrival(newest.id);
      window.setTimeout(() => setArrival(null), 1200);
    }
    setSnapshot(next);
  }), []);

  const activities = useMemo(() => snapshot.selfActivity.slice(0, 5), [snapshot.selfActivity]);
  const kind = sceneKind(snapshot);
  const primary = activities[0];

  return (
    <section className={`world-work-scene scene-${kind}`} aria-hidden="true">
      <div className="scene-floor" />
      <div className="scene-axis axis-x" />
      <div className="scene-axis axis-y" />

      <div className="scene-title">
        <span>{kind === 'quiet' ? 'PRESENT' : kind.toUpperCase()}</span>
        <b>{kind === 'quiet' ? 'JARVIS is with you' : snapshot.currentFocus}</b>
      </div>

      <div className="scene-intent">
        <i />
        <span>NOW</span>
        <b>{snapshot.currentFocus}</b>
      </div>

      <div className="scene-workplane">
        <div className="workplane-core" />
        {activities.map((item, index) => {
          const newest = item.id === arrival;
          return (
            <div
              key={item.id}
              className={`scene-artifact artifact-${activityRole(item)} ${newest ? 'arriving' : ''} ${index === 0 ? 'current-artifact' : ''}`}
              style={{ '--scene-index': index } as CSSProperties}
            >
              <span className="artifact-wire" />
              <i />
              <div>
                <small>{item.kind}</small>
                <b>{item.title}</b>
                <p>{item.detail}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="scene-companion">
        <div className="companion-presence">
          <span />
          <i />
        </div>
        <div>
          <small>{primary ? 'CURRENT WORK' : 'STANDING BY'}</small>
          <b>{primary?.title ?? 'JARVIS is maintaining context'}</b>
        </div>
      </div>
    </section>
  );
}
