import { JarvisSignal } from './signalPrioritizer';

const STORAGE_KEY = 'jarvis.signal-history.v1';
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

interface SignalMemoryEntry { fingerprint: string; shownAt: number; }
interface SignalMemoryState { current?: SignalMemoryEntry; history: SignalMemoryEntry[]; }

function fingerprint(signal: JarvisSignal): string {
  return `${signal.kind}|${signal.message}`;
}

function read(): SignalMemoryState {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return { history: [] };
    const parsed = JSON.parse(raw) as Partial<SignalMemoryState>;
    const history = Array.isArray(parsed.history)
      ? parsed.history.filter((entry): entry is SignalMemoryEntry =>
        !!entry && typeof entry.fingerprint === 'string' && typeof entry.shownAt === 'number')
      : [];
    return { current: parsed.current, history: history.slice(-MAX_HISTORY) };
  } catch {
    return { history: [] };
  }
}

function write(state: SignalMemoryState) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Signal memory is advisory; a storage failure must not affect the interface.
  }
}

function lastShown(state: SignalMemoryState, fingerprintValue: string): number | undefined {
  return state.history.findLast((entry) => entry.fingerprint === fingerprintValue)?.shownAt;
}

export function deriveTemporalJarvisSignal(candidates: JarvisSignal[], now = Date.now()): JarvisSignal {
  const state = read();
  const top = candidates[0];
  if (!top) return { kind: 'QUIET', score: 0, message: 'Nothing currently needs your attention.' };

  const topFingerprint = fingerprint(top);
  const current = state.current;

  if (current?.fingerprint === topFingerprint && now - current.shownAt < DWELL_MS) return top;

  const eligible = candidates.find((candidate) => {
    const seen = lastShown(state, fingerprint(candidate));
    return seen === undefined || now - seen >= SUPPRESSION_MS[candidate.kind];
  });

  const selected = eligible ?? top;
  const selectedFingerprint = fingerprint(selected);
  const seen = lastShown(state, selectedFingerprint);
  const severityChanged = current && current.fingerprint !== selectedFingerprint && selected.score > top.score;

  if (seen === undefined || now - seen >= SUPPRESSION_MS[selected.kind] || severityChanged || current?.fingerprint !== selectedFingerprint) {
    const entry = { fingerprint: selectedFingerprint, shownAt: now };
    const nextHistory = state.history.filter((item) => item.fingerprint !== selectedFingerprint).concat(entry).slice(-MAX_HISTORY);
    write({ current: entry, history: nextHistory });
  }

  return selected;
}
