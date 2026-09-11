import React from 'react';
import { createRoot } from 'react-dom/client';
import AppWorld from './JarvisWorldPrototype';
import JarvisWorldGuide from './JarvisWorldGuide';
import './jarvis-world-prototype.css';
import './jarvis-world-prototype-refinement.css';
import './jarvis-world-guide.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppWorld />
    <JarvisWorldGuide />
  </React.StrictMode>,
);
