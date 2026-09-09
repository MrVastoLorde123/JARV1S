import type { JarvisSnapshot } from './contracts';

export interface JarvisCommand {
  text: string;
  sessionId: string;
}

export interface JarvisActivityEvent {
  id: string;
  kind: string;
  title: string;
  detail: string;
  timestamp: string;
}

export interface JarvisGateway {
  snapshot(sessionId: string): Promise<JarvisSnapshot>;
  submit(command: JarvisCommand): Promise<JarvisActivityEvent>;
  subscribe(sessionId: string, onEvent: (event: JarvisActivityEvent) => void): () => void;
}

export const gatewayContract = {
  transport: 'HTTP + event stream',
  implementation: 'replaceable',
  knowsPythonInternals: false,
} as const;