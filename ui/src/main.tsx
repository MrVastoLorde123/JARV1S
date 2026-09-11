import React from 'react';
import { createRoot } from 'react-dom/client';
import AppWorld from './JarvisWorldPrototype';
import JarvisWorldGuide from './JarvisWorldGuide';
import JarvisWorldWorkScene from './JarvisWorldWorkScene';
import './jarvis-world-prototype.css';
import './jarvis-world-prototype-refinement.css';
import './jarvis-world-guide.css';
import './jarvis-world-follow.css';
import './jarvis-world-work-scene.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppWorld />
    <JarvisWorldWorkScene />
    <JarvisWorldGuide />
  </React.StrictMode>,
);
