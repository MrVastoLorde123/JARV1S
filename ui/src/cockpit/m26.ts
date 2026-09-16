export const M26_ACTIVITY_EVIDENCE_SCHEMA = "m26.activity_evidence.v1" as const;

export type ActivityStatus = "PENDING" | "RUNNING" | "SUCCEEDED" | "FAILED" | "BLOCKED" | "UNKNOWN";

export type ActivityStage =
  | "REQUEST"
  | "UNDERSTANDING"
  | "PROPOSAL"
  | "AUTHORIZATION"
  | "EXECUTION"
  | "OBSERVATION"
  | "VERIFICATION"
  | "COMPLETION"
  | "ERROR"
  | "UNKNOWN";

export type CockpitActivityEvent = Readonly<{
  sequence: number;
  requestId: string;
  kind: string;
  stage: ActivityStage;
  status: ActivityStatus;
  summary: string;
  observedAt: string | null;
}>;

export type CockpitEvidenceReference = Readonly<{
  evidenceId: string;
  kind: string;
  status: "VERIFIED" | "FAILED" | "UNVERIFIED" | "UNKNOWN";
  summary: string;
  observedAt: string | null;
  sourceEventSequence: number | null;
}>;

export type ActivityEvidenceState = Readonly<{
  schema: typeof M26_ACTIVITY_EVIDENCE_SCHEMA;
  cursor: number;
  activity: readonly CockpitActivityEvent[];
  evidence: readonly CockpitEvidenceReference[];
}>;

const STAGES = new Set<ActivityStage>([
  "REQUEST",
  "UNDERSTANDING",
  "PROPOSAL",
  "AUTHORIZATION",
  "EXECUTION",
  "OBSERVATION",
  "VERIFICATION",
  "COMPLETION",
  "ERROR",
  "UNKNOWN",
]);

const STATUSES = new Set<ActivityStatus>([
  "PENDING",
  "RUNNING",
  "SUCCEEDED",
  "FAILED",
  "BLOCKED",
  "UNKNOWN",
]);

function nonEmptyString(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : null;
}

export function normalizeSequence(value: unknown): number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0 ? value : 0;
}

export function normalizeObservedAt(value: unknown): string | null {
  const candidate = nonEmptyString(value);
  if (!candidate) return null;
  const parsed = Date.parse(candidate);
  return Number.isFinite(parsed) ? new Date(parsed).toISOString() : null;
}

export function normalizeActivityStatus(value: unknown): ActivityStatus {
  const candidate = typeof value === "string" ? value.trim().toUpperCase() : "";
  return STATUSES.has(candidate as ActivityStatus) ? (candidate as ActivityStatus) : "UNKNOWN";
}

export function normalizeActivityStage(value: unknown): ActivityStage {
  const candidate = typeof value === "string" ? value.trim().toUpperCase() : "";
  return STAGES.has(candidate as ActivityStage) ? (candidate as ActivityStage) : "UNKNOWN";
}

export function normalizeActivityEvent(value: unknown): CockpitActivityEvent | null {
  if (!value || typeof value !== "object") return null;
  const raw = value as Record<string, unknown>;
  const sequence = normalizeSequence(raw.sequence);
  const requestId = nonEmptyString(raw.request_id) ?? nonEmptyString(raw.requestId);
  const summary = nonEmptyString(raw.summary);
  const kind = nonEmptyString(raw.kind);
  if (!requestId || !summary || !kind) return null;
  return Object.freeze({
    sequence,
    requestId,
    kind,
    stage: normalizeActivityStage(raw.stage),
    status: normalizeActivityStatus(raw.status),
    summary,
    observedAt: normalizeObservedAt(raw.observed_at ?? raw.observedAt),
  });
}

export function normalizeEvidenceReference(value: unknown): CockpitEvidenceReference | null {
  if (!value || typeof value !== "object") return null;
  const raw = value as Record<string, unknown>;
  const evidenceId = nonEmptyString(raw.evidence_id) ?? nonEmptyString(raw.evidenceId);
  const kind = nonEmptyString(raw.kind);
  const summary = nonEmptyString(raw.summary);
  if (!evidenceId || !kind || !summary) return null;
  const statusCandidate = nonEmptyString(raw.status)?.toUpperCase();
  const status: CockpitEvidenceReference["status"] =
    statusCandidate === "VERIFIED" || statusCandidate === "FAILED" || statusCandidate === "UNVERIFIED" || statusCandidate === "UNKNOWN"
      ? (statusCandidate as CockpitEvidenceReference["status"])
      : "UNKNOWN";
  const source = raw.source_event_sequence ?? raw.sourceEventSequence;
  return Object.freeze({
    evidenceId,
    kind,
    status,
    summary,
    observedAt: normalizeObservedAt(raw.observed_at ?? raw.observedAt),
    sourceEventSequence: Number.isInteger(source) && Number(source) >= 0 ? Number(source) : null,
  });
}

export function createEmptyActivityEvidenceState(cursor = 0): ActivityEvidenceState {
  return Object.freeze({
    schema: M26_ACTIVITY_EVIDENCE_SCHEMA,
    cursor: normalizeSequence(cursor),
    activity: [],
    evidence: [],
  });
}

export function normalizeActivityWindow(value: unknown, fallbackCursor = 0): ActivityEvidenceState {
  if (!value || typeof value !== "object") return createEmptyActivityEvidenceState(fallbackCursor);
  const raw = value as Record<string, unknown>;
  const events = Array.isArray(raw.events) ? raw.events.map(normalizeActivityEvent).filter((event): event is CockpitActivityEvent => event !== null) : [];
  const evidence = Array.isArray(raw.evidence)
    ? raw.evidence.map(normalizeEvidenceReference).filter((item): item is CockpitEvidenceReference => item !== null)
    : [];
  return Object.freeze({
    schema: M26_ACTIVITY_EVIDENCE_SCHEMA,
    cursor: normalizeSequence(raw.cursor ?? fallbackCursor),
    activity: Object.freeze(events),
    evidence: Object.freeze(evidence),
  });
}
