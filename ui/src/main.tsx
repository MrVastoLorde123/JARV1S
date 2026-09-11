import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import AppWorld from './JarvisWorldPrototype';
import JarvisLandscape from './JarvisLandscape';
import JarvisWorldProcess from './JarvisWorldProcess';
import JarvisReturnBriefing from './JarvisReturnBriefing';
import './jarvis-world-prototype.css';
import './jarvis-world-prototype-refinement.css';
import './jarvis-landscape.css';
import './jarvis-world-breathing.css';
import './jarvis-world-process.css';
import './jarvis-landscape-physics.css';
import './jarvis-agent-travel.css';
import './jarvis-return-briefing.css';
import './jarvis-return-briefing-refinement.css';
import './jarvis-world-cleanup.css';

type LandscapeId = 'OPERATIONS' | 'MIND' | 'AGENTS' | 'MODELS' | 'CAPABILITIES' | 'WORK' | 'MARKET';

function WorldShell() {
  const [landscape, setLandscape] = useState<LandscapeId>('OPERATIONS');

  useEffect(() => {
    const onLandscapeChange = (event: Event) => {
      const next = (event as CustomEvent<LandscapeId>).detail;
      if (typeof next === 'string') setLandscape(next);
    };
    window.addEventListener('jarvis:landscape', onLandscapeChange);
    return () => window.removeEventListener('jarvis:landscape', onLandscapeChange);
  }, []);

  return (
    <div className={`jarvis-world-shell field-${landscape.toLowerCase()}`}>
      <div className="jarvis-legacy-layer">
        <AppWorld />
        <JarvisWorldProcess />
        <JarvisReturnBriefing />
      </div>
      <JarvisLandscape />
    </div>
  );
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WorldShell />
  </React.StrictMode>,
);
