import { JarvisSignal } from './signalPrioritizer';

const STORAGE_KEY = 'jarvis.signal-history.v2';
const MAX_HISTORY = 24;
const DWELL_MS = 10_000;
const SUPPRESSION_MS: Record<JarvisSignal['kind'], number> = {
  CRITICAL: 15_000,
  ATTENTION: 45_000,
  PRESSURE: 30_000,
  PROGRESS: 60_000,
  CONTEXT: 90_000,
  QUIET: 15_000,
};

export type SignalInteractionState = 'SURFACED' | 'ACKNOWLEDGED' | 'RESOLVED';

export interface SignalMemoryEntry {
  fingerprint: string;
  shownAt: number;
  state: SignalInteractionState;
  acknowledgedAt?: number;
  resolvedAt?: number;
}

interface SignalMemoryState { current?: SignalMemoryEntry; history: SignalMemoryEntry[]; }

function fingerprint(signal: JarvisSignal): string {
  return `${signal.kind}|${signal.message}`;
}

function findLastEntry(history: SignalMemoryEntry[], fingerprintValue: string): SignalMemoryEntry | undefined {
  for (let index = history.length - 1; index >= 0; index -= 1) {
    const entry = history[index];
    if (entry.fingerprint === fingerprintValue) return entry;
  }
  return undefined;
}

function read(): SignalMemoryState {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return { history: [] };
    const parsed = JSON.parse(raw) as Partial<SignalMemoryState>;
    const history = Array.isArray(parsed.history)
      ? parsed.history.filter((entry): entry is SignalMemoryEntry =>
        !!entry && typeof entry.fingerprint === 'string' && typeof entry.shownAt === 'number'
        && (entry.state === 'SURFACED' || entry.state === 'ACKNOWLEDGED' || entry.state === 'RESOLVED'))
      : [];
    const current = parsed.current && typeof parsed.current.fingerprint === 'string' && typeof parsed.current.shownAt === 'number'
      && (parsed.current.state === 'SURFACED' || parsed.current.state === 'ACKNOWLEDGED' || parsed.current.state === 'RESOLVED')
      ? parsed.current
      : undefined;
    return { current, history: history.slice(-MAX_HISTORY) };
  } catch {
    return { history: [] };
  }
}

function write(state: SignalMemoryState) {
  try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch {
    // Signal interaction memory is advisory; storage failure must not affect the interface.
  }
}

function saveEntry(state: SignalMemoryState, entry: SignalMemoryEntry) {
  const history = state.history.filter((item) => item.fingerprint !== entry.fingerprint).concat(entry).slice(-MAX_HISTORY);
  write({ current: entry, history });
}

function lastShown(state: SignalMemoryState, fingerprintValue: string): number | undefined {
  return findLastEntry(state.history, fingerprintValue)?.shownAt;
}

export function deriveTemporalJarvisSignal(candidates: JarvisSignal[], now = Date.now()): JarvisSignal {
  const state = read();
  const top = candidates[0];
  if (!top) return { kind: 'QUIET', score: 0, message: 'Nothing currently needs your attention.' };

  const topFingerprint = fingerprint(top);
  const current = state.current;
  if (current?.fingerprint === topFingerprint && now - current.shownAt < DWELL_MS) return top;

  const eligible = candidates.find((candidate) => {
    const candidateFingerprint = fingerprint(candidate);
    const seen = lastShown(state, candidateFingerprint);
    const entry = findLastEntry(state.history, candidateFingerprint);
    if (entry?.state === 'RESOLVED' && seen !== undefined && now - seen < SUPPRESSION_MS[candidate.kind] * 2) return false;
    return seen === undefined || now - seen >= SUPPRESSION_MS[candidate.kind];
  });

  const selected = eligible ?? top;
  const selectedFingerprint = fingerprint(selected);
  if (current?.fingerprint !== selectedFingerprint) {
    const entry = { fingerprint: selectedFingerprint, shownAt: now, state: 'SURFACED' as const };
    saveEntry(state, entry);
  }

  return selected;
}

export function getCurrentSignal(): JarvisSignal | undefined {
  const current = read().current;
  if (!current) return undefined;
  const separator = current.fingerprint.indexOf('|');
  if (separator < 1) return undefined;
  const kind = current.fingerprint.slice(0, separator) as JarvisSignal['kind'];
  const message = current.fingerprint.slice(separator + 1);
  return { kind, message, score: 0 };
}

export function getSignalInteraction(signal: JarvisSignal): SignalInteractionState {
  const entry = findLastEntry(read().history, fingerprint(signal));
  return entry?.state ?? 'SURFACED';
}

export function acknowledgeSignal(signal: JarvisSignal, now = Date.now()): void {
  const state = read();
  const id = fingerprint(signal);
  const previous = findLastEntry(state.history, id);
  const entry: SignalMemoryEntry = {
    ...(previous ?? { fingerprint: id, shownAt: now }),
    state: 'ACKNOWLEDGED',
    acknowledgedAt: now,
  };
  saveEntry(state, entry);
}

export function resolveSignal(signal: JarvisSignal, now = Date.now()): void {
  const state = read();
  const id = fingerprint(signal);
  const previous = findLastEntry(state.history, id);
  const entry: SignalMemoryEntry = {
    ...(previous ?? { fingerprint: id, shownAt: now }),
    state: 'RESOLVED',
    acknowledgedAt: previous?.acknowledgedAt ?? now,
    resolvedAt: now,
  };
  saveEntry(state, entry);
}
