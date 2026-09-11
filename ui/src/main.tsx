import React from 'react';
import { createRoot } from 'react-dom/client';
import AppOS from './JarvisOSPrototype';
import './jarvis-os-prototype.css';
import './jarvis-os-prototype-refinement.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode><AppOS /></React.StrictMode>,
);
