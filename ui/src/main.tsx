import React from 'react';
import { createRoot } from 'react-dom/client';
import AppWorld from './JarvisWorldPrototype';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode><AppWorld /></React.StrictMode>,
);
