export const M25_LIVE_STATE_SCHEMA = "m25.live_system_state.v1" as const;

export type LiveStateAvailability = "READY" | "DEGRADED" | "UNAVAILABLE" | "UNKNOWN";
export type LiveTaskState = "IDLE" | "ACTIVE" | "BLOCKED" | "COMPLETE" | "UNKNOWN";
export type LiveVerificationState = "VERIFIED" | "FAILED" | "PENDING" | "UNKNOWN";

export type LiveSystemState = Readonly<{
  schema: typeof M25_LIVE_STATE_SCHEMA;
  observedAt: string | null;
  ageMs: number | null;
  availability: LiveStateAvailability;
  runtimeAvailable: boolean;
  readOnly: boolean;
  task: Readonly<{
    state: LiveTaskState;
    progress: number | null;
    source: string | null;
  }>;
  model: Readonly<{
    provider: string | null;
    model: string | null;
    state: string | null;
  }>;
  verification: Readonly<{
    state: LiveVerificationState;
    evidenceCount: number;
  }>;
  agents: Readonly<{
    active: number;
    listed: number;
  }>;
  blockers: readonly Readonly<{
    message: string;
    severity: string | null;
  }>[];
  cursor: number;
}>;

type ControlPlaneInput = {
  generated_at?: string;
  runtime?: { available?: boolean; read_only?: boolean };
  task?: { state?: string; progress?: number; source?: string };
  agents?: Array<unknown>;
  model?: { provider?: string; model?: string; state?: string };
  blockers?: Array<{ message?: string; severity?: string }>;
  verification?: { state?: string; evidence?: unknown[] };
  cursor?: number;
};

function normalizeProgress(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return Math.min(1, Math.max(0, value));
}

function normalizeTaskState(value: unknown): LiveTaskState {
  return value === "IDLE" || value === "ACTIVE" || value === "BLOCKED" || value === "COMPLETE" ? value : "UNKNOWN";
}

function normalizeVerificationState(value: unknown): LiveVerificationState {
  return value === "VERIFIED" || value === "FAILED" || value === "PENDING" ? value : "UNKNOWN";
}

function normalizeString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function normalizeCursor(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? Math.floor(value) : 0;
}

export function buildLiveSystemState(input: ControlPlaneInput | null, now = Date.now()): LiveSystemState {
  const generatedAt = normalizeString(input?.generated_at);
  const observedAtMs = generatedAt ? Date.parse(generatedAt) : Number.NaN;
  const ageMs = Number.isFinite(observedAtMs) ? Math.max(0, now - observedAtMs) : null;
  const runtimeAvailable = input?.runtime?.available === true;
  const readOnly = input?.runtime?.read_only !== false;
  const blockers = Array.isArray(input?.blockers)
    ? input.blockers.map((blocker) => ({ message: normalizeString(blocker?.message) ?? "Unknown blocker", severity: normalizeString(blocker?.severity) }))
    : [];
  const listedAgents = Array.isArray(input?.agents) ? input.agents.length : 0;
  const taskState = normalizeTaskState(input?.task?.state);
  const verificationState = normalizeVerificationState(input?.verification?.state);
  const availability: LiveStateAvailability = !input
    ? "UNKNOWN"
    : !runtimeAvailable
      ? "UNAVAILABLE"
      : blockers.length > 0 || taskState === "BLOCKED"
        ? "DEGRADED"
        : "READY";

  return {
    schema: M25_LIVE_STATE_SCHEMA,
    observedAt: generatedAt,
    ageMs,
    availability,
    runtimeAvailable,
    readOnly,
    task: {
      state: taskState,
      progress: normalizeProgress(input?.task?.progress),
      source: normalizeString(input?.task?.source),
    },
    model: {
      provider: normalizeString(input?.model?.provider),
      model: normalizeString(input?.model?.model),
      state: normalizeString(input?.model?.state),
    },
    verification: {
      state: verificationState,
      evidenceCount: Array.isArray(input?.verification?.evidence) ? input.verification.evidence.length : 0,
    },
    agents: {
      active: listedAgents,
      listed: listedAgents,
    },
    blockers,
    cursor: normalizeCursor(input?.cursor),
  };
}

export function isLiveStateFresh(state: LiveSystemState, maxAgeMs = 10_000, now = Date.now()): boolean {
  if (state.observedAt === null) return false;
  const observedAtMs = Date.parse(state.observedAt);
  if (!Number.isFinite(observedAtMs) || maxAgeMs < 0) return false;
  return now - observedAtMs <= maxAgeMs;
}

export function createUnknownLiveSystemState(): LiveSystemState {
  return buildLiveSystemState(null);
}
