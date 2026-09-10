import { JarvisSnapshot, ProjectContract } from './contracts';

export type SignalKind = 'CRITICAL' | 'ATTENTION' | 'PRESSURE' | 'PROGRESS' | 'CONTEXT' | 'QUIET';

export interface JarvisSignal {
  kind: SignalKind;
  message: string;
  score: number;
}

function activeProject(snapshot: JarvisSnapshot): ProjectContract | undefined {
  return snapshot.projects.find((project) => project.state === 'ACTIVE');
}

function pausedProject(snapshot: JarvisSnapshot): ProjectContract | undefined {
  return snapshot.projects.find((project) => project.state === 'PAUSED');
}

function waitingProject(snapshot: JarvisSnapshot): ProjectContract | undefined {
  return snapshot.projects.find((project) => project.state === 'WAITING');
}

function bestSignal(snapshot: JarvisSnapshot): JarvisSignal {
  const candidates: JarvisSignal[] = [];

  if (!snapshot.online) {
    candidates.push({ kind: 'CRITICAL', score: 1000, message: 'Core connectivity requires attention.' });
  }

  if (snapshot.attentionRequired) {
    candidates.push({ kind: 'ATTENTION', score: 900, message: snapshot.attentionReason });
  }

  if (snapshot.resources.pressure === 'HIGH') {
    candidates.push({
      kind: 'PRESSURE',
      score: 800,
      message: `Resource pressure is high: ${snapshot.resources.cpuLoad}% CPU / ${snapshot.resources.memoryLoad}% memory.`,
    });
  }

  const paused = pausedProject(snapshot);
  if (paused) {
    candidates.push({
      kind: 'ATTENTION',
      score: 650,
      message: `Project paused: ${paused.name}.`,
    });
  }

  if (snapshot.resources.pressure === 'ELEVATED') {
    candidates.push({
      kind: 'PRESSURE',
      score: 600,
      message: `Resource pressure is elevated: ${snapshot.resources.cpuLoad}% CPU / ${snapshot.resources.memoryLoad}% memory.`,
    });
  }

  const waiting = waitingProject(snapshot);
  if (waiting) {
    candidates.push({
      kind: 'CONTEXT',
      score: 500,
      message: `Project waiting: ${waiting.name}${waiting.currentAction ? ` — ${waiting.currentAction}` : '.'}`,
    });
  }

  const active = activeProject(snapshot);
  if (active) {
    const progress = typeof active.progress === 'number' ? ` · ${active.progress}%` : '';
    candidates.push({
      kind: 'PROGRESS',
      score: 400,
      message: `Active project: ${active.name}${progress}.`,
    });
  }

  const activePlan = snapshot.plans.find((plan) => plan.state === 'IN_PROGRESS');
  if (activePlan) {
    const step = typeof activePlan.currentStep === 'number' && activePlan.steps[activePlan.currentStep - 1]
      ? ` · Step ${activePlan.currentStep}: ${activePlan.steps[activePlan.currentStep - 1]}`
      : '';
    candidates.push({ kind: 'PROGRESS', score: 350, message: `Plan in progress: ${activePlan.title}${step}.` });
  }

  const research = snapshot.researchTopics.find((topic) => topic.state === 'ACTIVE' && topic.lastThought);
  if (research?.lastThought) {
    candidates.push({
      kind: 'CONTEXT',
      score: 300,
      message: `Research signal: ${research.lastThought}`,
    });
  }

  if (snapshot.mode === 'Learning') {
    candidates.push({ kind: 'CONTEXT', score: 250, message: `Context is being updated from: ${snapshot.currentFocus}.` });
  }

  if (snapshot.mode === 'Thinking') {
    candidates.push({ kind: 'CONTEXT', score: 200, message: `Interpreting: ${snapshot.currentFocus}.` });
  }

  if (snapshot.mode === 'Working' && active) {
    candidates.push({ kind: 'PROGRESS', score: 220, message: `Project procedure active: ${active.name}.` });
  }

  if (candidates.length === 0) {
    return { kind: 'QUIET', score: 0, message: 'Nothing currently needs your attention.' };
  }

  return candidates.sort((left, right) => right.score - left.score)[0];
}

export function deriveJarvisSignal(snapshot: JarvisSnapshot): JarvisSignal {
  return bestSignal(snapshot);
}
