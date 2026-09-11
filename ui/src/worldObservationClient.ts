export interface InterfaceResponseEnvelope {
  request_id: string;
  content: string;
  metadata: Record<string, unknown>;
  authority_granted: false;
  authorization_granted: false;
  execution_requested: false;
}

export interface WorldAgentObservation {
  agent: {
    agent_id: string;
    display_name: string;
    archetype: string;
    assignment_id: string;
    status: string;
    landscape: string;
    destination: string | null;
    model_id: string | null;
    capability_ids: string[];
    created_at: string;
    updated_at: string;
    metadata: Record<string, unknown>;
    authority_granted: false;
    permissions_granted: false;
  };
  route: Record<string, unknown> | null;
  lineage: Record<string, unknown> | null;
  evidence: Record<string, unknown> | null;
  handoff: Record<string, unknown> | null;
  active: boolean;
}

export interface WorldObservationPayload {
  schema: 'm28.13.world_observation';
  request_id: string;
  session_id: string | null;
  world: {
    generated_at: string;
    agents: WorldAgentObservation[];
    focused_agent_id: string | null;
    current_landscape: string;
    active_agent_count: number;
    landscape_counts: Record<string, number>;
    metadata: Record<string, unknown>;
    authority_granted: false;
    permissions_granted: false;
  };
  metadata: Record<string, unknown>;
  authority_granted: false;
  authorization_granted: false;
  execution_requested: false;
  policy_mutation: false;
}

export interface WorldObservationResponse {
  envelope: InterfaceResponseEnvelope;
  observation: WorldObservationPayload;
}

export interface WorldObservationClientOptions {
  endpoint?: string;
  sessionId?: string;
  signal?: AbortSignal;
}

export async function fetchWorldObservation(
  options: WorldObservationClientOptions = {},
): Promise<WorldObservationResponse> {
  const endpoint = options.endpoint ?? '/api/world/observation';
  const headers: Record<string, string> = { Accept: 'application/json' };
  if (options.sessionId) headers['X-JARVIS-Session-ID'] = options.sessionId;

  const response = await fetch(endpoint, {
    method: 'GET',
    headers,
    cache: 'no-store',
    signal: options.signal,
  });

  if (!response.ok) {
    throw new Error(`JARVIS world observation request failed: HTTP ${response.status}`);
  }

  const envelope = (await response.json()) as InterfaceResponseEnvelope;
  const observation = JSON.parse(envelope.content) as WorldObservationPayload;

  if (observation.schema !== 'm28.13.world_observation') {
    throw new Error(`Unsupported world observation schema: ${String(observation.schema)}`);
  }

  if (envelope.metadata.interface_payload !== 'WORLD_OBSERVATION') {
    throw new Error('Unexpected interface payload; expected WORLD_OBSERVATION.');
  }

  if (!Array.isArray(observation.world.agents)) {
    throw new Error('Invalid world observation: agents must be an array.');
  }

  return { envelope, observation };
}
