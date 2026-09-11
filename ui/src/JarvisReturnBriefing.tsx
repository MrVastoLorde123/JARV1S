import { useEffect, useRef, useState } from 'react';
import { demoGateway } from './demoGateway';
import type { JarvisSnapshot } from './contracts';

function summarize(snapshot: JarvisSnapshot, previous: JarvisSnapshot | null) {
  if (!previous) return null;
  const currentIds = new Set(snapshot.selfActivity.map((item) => item.id));
  const newSignals = snapshot.selfActivity.filter((item) => !new Set(previous.selfActivity.map((entry) => entry.id)).has(item.id));
  const active = snapshot.projects.filter((project) => project.state === 'ACTIVE').length;
  const completed = snapshot.projects.filter((project) => project.state === 'COMPLETED').length - previous.projects.filter((project) => project.state === 'COMPLETED').length;
  const latest = newSignals[0] ?? snapshot.selfActivity[0];
  const learning = snapshot.researchTopics.filter((topic) => topic.thoughtCount > 0).length;
  const next = snapshot.projects.find((project) => project.state === 'ACTIVE') ?? snapshot.projects.find((project) => project.state === 'WAITING');
  void currentIds;
  return {
    newSignals: newSignals.length,
    active,
    completed: Math.max(0, completed),
    latest: latest?.title ?? 'JARVIS maintained the current context',
    focus: snapshot.currentFocus,
    learning,
    next: next?.currentAction ?? 'Standing by for the next meaningful transition',
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
      window.setTimeout(() => setBriefing(null), 7200);
    };
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, []);

  if (!briefing) return null;
  return (
    <aside className="jarvis-return-briefing" aria-live="polite">
      <div className="briefing-presence"><span />J</div>
      <div className="briefing-copy">
        <span>JARVIS / RETURN STATE</span>
        <b>Welcome back, Jero. Here is what moved while you were away.</b>
        <div className="briefing-facts">
          <article><small>NEW ACTIVITY</small><strong>{briefing.newSignals}</strong></article>
          <article><small>ACTIVE WORK</small><strong>{briefing.active}</strong></article>
          <article><small>KNOWLEDGE THREADS</small><strong>{briefing.learning}</strong></article>
        </div>
        <p><b>Achievement:</b> {briefing.latest}. <b>Now:</b> {briefing.focus}. <b>Next:</b> {briefing.next}.</p>
      </div>
    </aside>
  );
}
