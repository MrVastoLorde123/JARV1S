import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { installThemeController } from './themeController';
import { installDesktopPresence } from './desktopPresenceController';
import { installProjectLanguage } from './projectLanguageController';
import { installSelfRuntime } from './self-runtime-controller-m27.30';
import './styles.css';
import './mission.css';
import './identity.css';
import './theme.css';
import './mission-spine.css';
import './desktop-presence.css';
import './readability.css';
import './interface-polish.css';
import './interface-refinement-m27.27.css';
import './mission-flow-m27.28.css';
import './live-missions-footer-m27.30.css';
import './runtime-state-expression-m27.30.css';
import './self-runtime-m27.30.css';
import './sidebar-refinement-m27.30.css';
import './self-runtime-host-m27.30.css';
import './mission-surface-pruning-m27.31.css';
import './self-execution-thread-m27.31.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>,
);

installThemeController();
installDesktopPresence();
installProjectLanguage();
installSelfRuntime();
