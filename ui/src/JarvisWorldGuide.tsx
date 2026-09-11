import { useEffect, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';
import './jarvis-world-guide.css';

function guidance(snapshot: JarvisSnapshot) {
  if (!snapshot.online) return { kind: 'OFFLINE', label: 'JARVIS', message: 'The world remains, but my core is unavailable.', target: 'CORE' };
  if (snapshot.attentionRequired || snapshot.mode === 'Needs You') return { kind: 'ATTENTION', label: 'I need you here', message: snapshot.attentionReason || 'A decision is waiting for you.', target: 'ATTENTION' };
  if (snapshot.mode === 'Working') {
    const mission = snapshot.projects.find((project) => project.state === 'ACTIVE') ?? snapshot.projects[0];
    return { kind: 'WORKING', label: 'Come with me', message: mission?.currentAction ?? 'I am working on the current mission.', target: 'MISSION' };
  }
  if (snapshot.mode === 'Thinking') return { kind: 'THINKING', label: 'Stay with me', message: snapshot.currentFocus, target: 'CONTEXT' };
  if (snapshot.mode === 'Learning') return { kind: 'LEARNING', label: 'Look at this with me', message: snapshot.researchTopics[0]?.title ?? 'I am connecting what I have learned.', target: 'CONTEXT' };
  if (snapshot.mode === 'Monitoring') return { kind: 'MONITORING', label: 'Watch this with me', message: `${snapshot.resources.pressure} pressure · ${snapshot.monitoredSources} monitored sources`, target: 'RUNTIME' };
  return { kind: 'WAITING', label: 'JARVIS is with you', message: snapshot.currentFocus, target: 'CORE' };
}

export default function JarvisWorldGuide() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());

  useEffect(() => demoGateway.subscribe('jarvis-world-guide', () => setSnapshot(demoGateway.snapshotSync())), []);

  const guide = guidance(snapshot);
  const visible = guide.kind !== 'WAITING' || snapshot.attentionRequired;

  useEffect(() => {
    const root = document.documentElement;
    root.dataset.jarvisFollow = guide.target.toLowerCase();
    root.dataset.jarvisGuideKind = guide.kind.toLowerCase();
    root.dataset.jarvisJourney = 'entering';
    const timeout = window.setTimeout(() => { root.dataset.jarvisJourney = 'settled'; }, 1050);
    return () => window.clearTimeout(timeout);
  }, [guide.target, guide.kind]);

  return (
    <div className={`jarvis-world-guide guide-${guide.kind.toLowerCase()} target-${guide.target.toLowerCase()} ${visible ? 'guide-visible' : ''}`} aria-live="polite">
      <div className="guide-thread" />
      <div className="guide-beacon"><i /><span /></div>
      {visible && <div className="guide-caption"><span>{guide.label}</span><b>{guide.message}</b></div>}
    </div>
  );
}
