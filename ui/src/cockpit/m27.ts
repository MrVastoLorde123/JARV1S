export const M27_INTERACTION_SCHEMA = "m27.interaction.v1" as const;

export const INTERACTION_STATES = [
  "IDLE",
  "COMPOSING",
  "SUBMITTING",
  "PROCESSING",
  "RESPONDED",
  "FAILED",
] as const;

export type InteractionState = (typeof INTERACTION_STATES)[number];

export type InteractionRequest = Readonly<{
  requestId: string;
  sessionId: string;
  content: string;
  submittedAt: string;
}>;

export type InteractionResponse = Readonly<{
  requestId: string | null;
  content: string;
  receivedAt: string;
}>;

export type InteractionError = Readonly<{
  requestId: string | null;
  message: string;
  failedAt: string;
}>;

export type InteractionStateSnapshot = Readonly<{
  schema: typeof M27_INTERACTION_SCHEMA;
  state: InteractionState;
  request: InteractionRequest | null;
  response: InteractionResponse | null;
  error: InteractionError | null;
  explicitSubmission: boolean;
  automaticExecution: false;
}>;

function nonEmpty(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const normalized = value.trim();
  return normalized.length > 0 ? normalized : null;
}

export function isInteractionState(value: unknown): value is InteractionState {
  return typeof value === "string" && (INTERACTION_STATES as readonly string[]).includes(value);
}

export function normalizeInteractionContent(value: unknown): string {
  return nonEmpty(value) ?? "";
}

export function normalizeRequestId(value: unknown): string | null {
  return nonEmpty(value);
}

export function createInteractionSnapshot(
  state: InteractionState = "IDLE",
  request: InteractionRequest | null = null,
): InteractionStateSnapshot {
  if (!isInteractionState(state)) throw new TypeError("invalid interaction state");
  return Object.freeze({
    schema: M27_INTERACTION_SCHEMA,
    state,
    request,
    response: null,
    error: null,
    explicitSubmission: request !== null,
    automaticExecution: false,
  });
}

export function createInteractionRequest(
  content: unknown,
  now: string,
  sessionId = "desktop",
  requestId?: string,
): InteractionRequest | null {
  const normalizedContent = nonEmpty(content);
  const normalizedSession = nonEmpty(sessionId);
  const normalizedTime = nonEmpty(now);
  const normalizedRequestId = nonEmpty(requestId) ?? crypto.randomUUID();
  if (!normalizedContent || !normalizedSession || !normalizedTime) return null;
  return Object.freeze({
    requestId: normalizedRequestId,
    sessionId: normalizedSession,
    content: normalizedContent,
    submittedAt: normalizedTime,
  });
}

export function normalizeInteractionResponse(
  value: unknown,
  requestId: string | null,
  now: string,
): InteractionResponse | null {
  if (!value || typeof value !== "object") return null;
  const raw = value as Record<string, unknown>;
  const content = nonEmpty(raw.content);
  const receivedAt = nonEmpty(now);
  if (!content || !receivedAt) return null;
  return Object.freeze({
    requestId: normalizeRequestId(raw.request_id ?? raw.requestId) ?? requestId,
    content,
    receivedAt,
  });
}

export function createInteractionError(
  value: unknown,
  requestId: string | null,
  now: string,
): InteractionError {
  const message = nonEmpty(value) ?? "Unknown interaction error.";
  return Object.freeze({ requestId, message, failedAt: nonEmpty(now) ?? "UNKNOWN" });
}
