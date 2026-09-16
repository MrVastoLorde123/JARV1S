export const M24_COCKPIT_SCHEMA = "m24.cockpit.v1" as const;

export const OPERATIONAL_STAGES = [
  "READY",
  "UNDERSTANDING",
  "GATHERING_EVIDENCE",
  "PROPOSING_ACTION",
  "WAITING_FOR_AUTHORIZATION",
  "EXECUTING",
  "VERIFYING",
  "COMPLETE",
  "BLOCKED",
] as const;

export type OperationalStage = (typeof OPERATIONAL_STAGES)[number];
export type ServiceHealth = "READY" | "UNAVAILABLE" | "UNKNOWN";
export type WorkStatus = "IDLE" | "ACTIVE" | "BLOCKED" | "COMPLETE";

export type CockpitActivity = Readonly<{
  sequence: number;
  timestamp: string;
  stage: OperationalStage;
  summary: string;
  durable: boolean;
}>;

export type CockpitWorkState = Readonly<{
  status: WorkStatus;
  objective: string | null;
  stage: OperationalStage;
  progress: number | null;
  activeAgentCount: number;
  blockerCount: number;
  lastVerifiedAt: string | null;
}>;

export type CockpitHealth = Readonly<{
  controlPlane: ServiceHealth;
  perception: ServiceHealth;
  capabilities: ServiceHealth;
  memory: ServiceHealth;
  verification: ServiceHealth;
}>;

export type CockpitSnapshot = Readonly<{
  schema: typeof M24_COCKPIT_SCHEMA;
  generatedAt: string;
  work: CockpitWorkState;
  health: CockpitHealth;
  activity: readonly CockpitActivity[];
  authority: Readonly<{ granted: boolean; permissionsGranted: boolean }>;
}>;

export function normalizeProgress(value: number | null | undefined): number | null {
  if (value === null || value === undefined || !Number.isFinite(value)) return null;
  return Math.min(1, Math.max(0, value));
}

export function isOperationalStage(value: unknown): value is OperationalStage {
  return typeof value === "string" && (OPERATIONAL_STAGES as readonly string[]).includes(value);
}

export function createIdleWorkState(): CockpitWorkState {
  return Object.freeze({ status: "IDLE", objective: null, stage: "READY", progress: 0, activeAgentCount: 0, blockerCount: 0, lastVerifiedAt: null });
}

export function createEmptyCockpitSnapshot(now = new Date().toISOString()): CockpitSnapshot {
  return Object.freeze({
    schema: M24_COCKPIT_SCHEMA,
    generatedAt: now,
    work: createIdleWorkState(),
    health: Object.freeze({ controlPlane: "UNKNOWN", perception: "UNKNOWN", capabilities: "UNKNOWN", memory: "UNKNOWN", verification: "UNKNOWN" }),
    activity: Object.freeze([]),
    authority: Object.freeze({ granted: false, permissionsGranted: false }),
  });
}
