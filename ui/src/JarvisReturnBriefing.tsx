import { useEffect, useRef, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

function summarize(snapshot: JarvisSnapshot, previous: JarvisSnapshot | null) {
  if (!previous) return null;
  const newSignals = Math.max(0, snapshot.selfActivity.length - previous.selfActivity.length);
  const active = snapshot.projects.filter((project) => project.state === 'ACTIVE').length;
  const latest = snapshot.selfActivity[0];
  return {
    newSignals,
    active,
    latest: latest?.title ?? 'JARVIS maintained the current context',
    focus: snapshot.currentFocus,
  };
}

export default function JarvisReturnBriefing() {
  const [briefing, setBriefing] = useState<ReturnType<typeof summarize>>(null);
  const lastSnapshot = useRef<JarvisSnapshot | null>(null);
  const awayAt = useRef<number | null>(null);

  useEffect(() => {
    lastSnapshot.current = demoGateway.snapshotSync();
    const onVisibility = () => {
      if (document.visibilityState === 'hidden') {
        awayAt.current = Date.now();
        return;
      }
      if (awayAt.current === null) return;
      const previous = lastSnapshot.current;
      const current = demoGateway.snapshotSync();
      const summary = summarize(current, previous);
      const awaySeconds = Math.round((Date.now() - awayAt.current) / 1000);
      awayAt.current = null;
      lastSnapshot.current = current;
      if (!summary || awaySeconds < 4) return;
      setBriefing(summary);
      window.setTimeout(() => setBriefing(null), 5200);
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, []);

  if (!briefing) return null;
  return (
    <aside className="jarvis-return-briefing" aria-live="polite">
      <div className="briefing-presence"><span />J</div>
      <div className="briefing-copy">
        <span>WELCOME BACK, JERO</span>
        <b>I kept working while you were away.</b>
        <p>{briefing.latest}. Current focus: {briefing.focus}. {briefing.active} active mission{briefing.active === 1 ? '' : 's'}.</p>
      </div>
    </aside>
  );
}
