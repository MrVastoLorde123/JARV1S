import type { JarvisSnapshot, SelfActivityContract } from './contracts';

export type MissionStageId = 'OBSERVE' | 'REASON' | 'ASSIGN' | 'EXECUTE' | 'VERIFY';
export type MissionStageStatus = 'ACTIVE' | 'READY' | 'ATTENTION' | 'GUARDED';

export interface MissionFlowStage {
  id: MissionStageId;
  label: string;
  detail: string;
  status: MissionStageStatus;
}

export interface MissionFlowState {
  stage: MissionStageId;
  status: 'ACTIVE' | 'STANDBY' | 'ATTENTION' | 'OFFLINE' | 'GUARDED';
  headline: string;
  evidence: string;
  guard: string;
  stages: MissionFlowStage[];
}

const stageOrder: MissionStageId[] = ['OBSERVE', 'REASON', 'ASSIGN', 'EXECUTE', 'VERIFY'];

function latestActivity(snapshot: JarvisSnapshot): SelfActivityContract | undefined {
  return snapshot.selfActivity[0];
}

function activeStage(snapshot: JarvisSnapshot): MissionStageId {
  const latest = latestActivity(snapshot);
  if (snapshot.mode === 'Thinking') return 'REASON';
  if (snapshot.mode === 'Learning') return 'VERIFY';
  if (snapshot.mode === 'Working') return latest?.kind === 'DELEGATING' ? 'ASSIGN' : 'EXECUTE';
  return 'OBSERVE';
}

function stageDetail(id: MissionStageId, snapshot: JarvisSnapshot, assignedModelName: string, latest: SelfActivityContract | undefined): string {
  if (id === 'OBSERVE') return snapshot.attentionRequired ? snapshot.attentionReason : `${snapshot.currentFocus} · ${snapshot.mode}`;
  if (id === 'REASON') return latest?.title ?? 'Evaluating context and constraints';
  if (id === 'ASSIGN') return latest?.detail ?? `${assignedModelName} is the active model lane`;
  if (id === 'EXECUTE') {
    const activeProject = snapshot.projects.find((project) => project.state === 'ACTIVE');
    return activeProject?.currentAction ?? snapshot.workRuntime.detail;
  }
  return latest?.detail ?? `Last state change · ${snapshot.lastStateChange}`;
}

export function deriveMissionFlowState(snapshot: JarvisSnapshot): MissionFlowState {
  const latest = latestActivity(snapshot);
  const assignedModel = snapshot.models.find((model) => model.state === 'ACTIVE') ?? snapshot.models[0];
  const current = activeStage(snapshot);
  const guarded = snapshot.resources.pressure === 'HIGH' || snapshot.resources.strategy === 'LIMITED_CONCURRENCY';
  const attention = snapshot.attentionRequired || snapshot.mode === 'Needs You';
  const status: MissionFlowState['status'] = !snapshot.online
    ? 'OFFLINE'
    : attention
      ? 'ATTENTION'
      : guarded
        ? 'GUARDED'
        : snapshot.mode === 'Waiting'
          ? 'STANDBY'
          : 'ACTIVE';

  const stages = stageOrder.map((id) => ({
    id,
    label: id === 'EXECUTE' ? 'EXECUTE' : id,
    detail: stageDetail(id, snapshot, assignedModel?.name ?? 'Standby', latest),
    status: id === current ? (attention ? 'ATTENTION' : guarded ? 'GUARDED' : 'ACTIVE') : 'READY',
  }));

  const headline = status === 'OFFLINE'
    ? 'Core unavailable'
    : status === 'ATTENTION'
      ? 'Your attention is required'
      : status === 'GUARDED'
        ? 'Operating under resource guard'
        : snapshot.mode === 'Waiting'
          ? 'Standing by for a meaningful transition'
          : `${current} is the current mission stage`;

  const evidence = latest?.title ?? snapshot.currentFocus;
  const guard = attention
    ? snapshot.attentionReason
    : guarded
      ? `${snapshot.resources.strategy} · ${snapshot.resources.activeModelTasks}/${snapshot.resources.concurrencyLimit} model task capacity`
      : `${assignedModel?.name ?? 'No active model'} · ${snapshot.workRuntime.state}`;

  return { stage: current, status, headline, evidence, guard, stages };
}
