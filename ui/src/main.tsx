import React from 'react';
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

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppWorld />
    <JarvisLandscape />
    <JarvisWorldProcess />
    <JarvisReturnBriefing />
  </React.StrictMode>,
);
