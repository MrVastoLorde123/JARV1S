import React from 'react';
import { createRoot } from 'react-dom/client';
import AppWorld from './JarvisWorldPrototype';
import JarvisWorldWorkScene from './JarvisWorldWorkScene';
import JarvisLandscape from './JarvisLandscape';
import JarvisWorldGuide from './JarvisWorldGuide';
import './jarvis-world-prototype.css';
import './jarvis-world-prototype-refinement.css';
import './jarvis-world-follow.css';
import './jarvis-world-work-scene.css';
import './jarvis-landscape.css';
import './jarvis-world-breathing.css';
import './jarvis-world-guide.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppWorld />
    <JarvisLandscape />
    <JarvisWorldWorkScene />
    <JarvisWorldGuide />
  </React.StrictMode>,
);
