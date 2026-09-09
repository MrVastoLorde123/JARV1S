import type { ReactNode } from 'react';

export type IconName = 'home' | 'chat' | 'projects' | 'mind' | 'capabilities' | 'self' | 'menu';

const paths: Record<IconName, ReactNode> = {
  home: <><path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V21h13V9.5"/><path d="M9 21v-6h6v6"/></>,
  chat: <><path d="M4 5.5h16v11H9l-5 4v-15Z"/><path d="M8 10h8M8 13h5"/></>,
  projects: <><path d="M4 7.5h6l2 2h8v9H4z"/><path d="M4 7.5V5h6l2 2"/></>,
  mind: <><circle cx="12" cy="12" r="2.5"/><circle cx="5" cy="7" r="1.8"/><circle cx="19" cy="7" r="1.8"/><circle cx="7" cy="18" r="1.8"/><circle cx="17" cy="18" r="1.8"/><path d="m10 10-3.5-2M14 10l3.5-2M10 14l-3 3M14 14l3 3"/></>,
  capabilities: <><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/><circle cx="12" cy="12" r="4.5"/></>,
  self: <><circle cx="12" cy="12" r="8.5"/><path d="M8.5 14.5c1 .9 2.2 1.4 3.5 1.4s2.5-.5 3.5-1.4M9 9.5h.01M15 9.5h.01"/><path d="M12 3.5V2"/></>,
  menu: <><path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/></>,
};

export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
