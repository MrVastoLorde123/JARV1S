import { demoGateway } from './demoGateway';
import { getJarvisSignalCandidates } from './signalPrioritizer';
import {
  acknowledgeSignal,
  deriveTemporalJarvisSignal,
  getSignalInteraction,
  resolveSignal,
} from './signalMemory';

const ID = 'jarvis-desktop-presence';

function ensurePresence() {
  let host = document.getElementById(ID);
  if (host) return host;

  host = document.createElement('section');
  host.id = ID;
  host.className = 'jarvis-desktop-presence';
  host.setAttribute('aria-label', 'JARVIS desktop presence');
  host.innerHTML = `
    <div class="desktop-presence-brand">
      <span class="presence-mark">J</span>
      <div><strong>JARVIS</strong><small>PERSONAL OPERATING ENVIRONMENT</small></div>
    </div>
    <div class="desktop-presence-context">
      <span data-presence="space">PROJECTS</span>
      <i></i>
      <span data-presence="focus">Awaiting context</span>
    </div>
    <div class="desktop-presence-state">
      <span class="presence-led" data-presence="led"></span>
      <div><b data-presence="mode">STANDING BY</b><small data-presence="event">Core connected</small></div>
    </div>
    <div class="desktop-presence-signal">
      <span>SIGNAL</span>
      <b data-presence="signal">Nothing currently needs your attention.</b>
      <div class="signal-actions" aria-label="Signal interaction">
        <button type="button" data-signal-action="acknowledge">SEEN</button>
        <button type="button" data-signal-action="resolve">HANDLED</button>
      </div>
    </div>
    <div class="desktop-presence-clock">
      <span data-presence="time">--:--:--</span>
      <small data-presence="uptime">UPTIME --:--:--</small>
    </div>
  `;

  host.querySelector<HTMLButtonElement>('[data-signal-action="acknowledge"]')?.addEventListener('click', () => {
    const snapshot = demoGateway.snapshotSync();
    acknowledgeSignal(deriveTemporalJarvisSignal(getJarvisSignalCandidates(snapshot)));
    update();
  });
  host.querySelector<HTMLButtonElement>('[data-signal-action="resolve"]')?.addEventListener('click', () => {
    const snapshot = demoGateway.snapshotSync();
    resolveSignal(deriveTemporalJarvisSignal(getJarvisSignalCandidates(snapshot)));
    update();
  });

  document.body.appendChild(host);
  return host;
}

function update() {
  const host = ensurePresence();
  const snapshot = demoGateway.snapshotSync();
  const signal = deriveTemporalJarvisSignal(getJarvisSignalCandidates(snapshot));
  const interaction = getSignalInteraction(signal);
  const currentSpace = document.querySelector('.top-context')?.textContent?.trim() || 'PROJECTS';
  const focus = document.querySelector('.top-focus')?.textContent?.trim() || snapshot.currentFocus;
  const event = document.querySelector('.state-pulse div small')?.textContent?.trim() || 'Core connected';

  host.querySelector<HTMLElement>('[data-presence="space"]')!.textContent = currentSpace;
  host.querySelector<HTMLElement>('[data-presence="focus"]')!.textContent = focus;
  host.querySelector<HTMLElement>('[data-presence="mode"]')!.textContent = snapshot.mode.toUpperCase();
  host.querySelector<HTMLElement>('[data-presence="event"]')!.textContent = event;
  host.querySelector<HTMLElement>('[data-presence="signal"]')!.textContent = signal.message;
  host.querySelector<HTMLElement>('[data-presence="uptime"]')!.textContent = `UPTIME ${snapshot.uptime}`;
  host.querySelector<HTMLElement>('[data-presence="time"]')!.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
  host.querySelector<HTMLElement>('[data-presence="led"]')!.className = `presence-led presence-${snapshot.mode.toLowerCase().replace(/\s+/g, '-')}`;

  const acknowledged = interaction === 'ACKNOWLEDGED' || interaction === 'RESOLVED';
  const resolved = interaction === 'RESOLVED';
  const seenButton = host.querySelector<HTMLButtonElement>('[data-signal-action="acknowledge"]')!;
  const handledButton = host.querySelector<HTMLButtonElement>('[data-signal-action="resolve"]')!;
  seenButton.disabled = acknowledged;
  seenButton.textContent = acknowledged ? 'SEEN ✓' : 'SEEN';
  handledButton.disabled = resolved;
  handledButton.textContent = resolved ? 'HANDLED ✓' : 'HANDLED';
  host.dataset.signalState = interaction.toLowerCase();
  host.dataset.signalKind = signal.kind.toLowerCase();
  host.dataset.pressure = snapshot.resources.pressure.toLowerCase();
  host.dataset.online = snapshot.online ? 'true' : 'false';
}

export function installDesktopPresence() {
  if (document.getElementById(ID)) return;
  ensurePresence();
  update();
  const unsubscribe = demoGateway.subscribe('desktop-presence', update);
  const timer = window.setInterval(update, 1000);
  window.addEventListener('beforeunload', () => {
    unsubscribe();
    window.clearInterval(timer);
  }, { once: true });
}
