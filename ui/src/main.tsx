import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { installThemeController } from './themeController';
import { installDesktopPresence } from './desktopPresenceController';
import './styles.css';
import './mission.css';
import './identity.css';
import './theme.css';
import './mission-spine.css';
import './desktop-presence.css';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>,
);

installThemeController();
installDesktopPresence();
