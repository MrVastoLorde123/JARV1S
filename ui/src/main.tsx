import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { installThemeController } from './themeController';
import './styles.css';
import './mission.css';
import './identity.css';
import './theme.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>,
);

installThemeController();
