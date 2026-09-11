import { useEffect, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';
import './jarvis-world-guide.css';

function guidance(snapshot: JarvisSnapshot) {
  if (!snapshot.online) return { kind: 'OFFLINE', label: 'JARVIS', message: 'The world remains, but my core is unavailable.', target: 'CORE' };
  if (snapshot.attentionRequired || snapshot.mode === 'Needs You') return { kind: 'ATTENTION', label: 'I need you here', message: snapshot.attentionReason || 'A decision is waiting for you.', target: 'ATTENTION' };
  if (snapshot.mode === 'Working') return { kind: 'WORKING', label: 'COME WITH ME', message: '', target: 'MISSION' };
  if (snapshot.mode === 'Thinking') return { kind: 'THINKING', label: 'STAY WITH ME', message: '', target: 'CONTEXT' };
  if (snapshot.mode === 'Learning') return { kind: 'LEARNING', label: 'LOOK WITH ME', message: '', target: 'CONTEXT' };
  if (snapshot.mode === 'Monitoring') return { kind: 'MONITORING', label: 'WATCH WITH ME', message: '', target: 'RUNTIME' };
  return { kind: 'WAITING', label: 'JARVIS IS WITH YOU', message: '', target: 'CORE' };
}

export default function JarvisWorldGuide() {
  const [snapshot, setSnapshot] = useState<JarvisSnapshot>(() => demoGateway.snapshotSync());

  useEffect(() => demoGateway.subscribe('jarvis-world-guide', () => setSnapshot(demoGateway.snapshotSync())), []);

  const guide = guidance(snapshot);
  const captionVisible = guide.kind === 'ATTENTION' || guide.kind === 'OFFLINE';

  useEffect(() => {
    const root = document.documentElement;
    root.dataset.jarvisFollow = guide.target.toLowerCase();
    root.dataset.jarvisGuideKind = guide.kind.toLowerCase();
    root.dataset.jarvisJourney = 'entering';
    const timeout = window.setTimeout(() => { root.dataset.jarvisJourney = 'settled'; }, 1050);
    return () => window.clearTimeout(timeout);
  }, [guide.target, guide.kind]);

  return (
    <div className={`jarvis-world-guide guide-${guide.kind.toLowerCase()} target-${guide.target.toLowerCase()} guide-visible`} aria-live="polite">
      <div className="guide-thread" />
      <div className="guide-beacon"><i /><span /></div>
      {captionVisible && <div className="guide-caption"><span>{guide.label}</span><b>{guide.message}</b></div>}
    </div>
  );
}
