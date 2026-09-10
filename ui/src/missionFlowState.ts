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
  projectId?: string;
  projectName?: string;
  workspaceName?: string;
  modelName?: string;
  headline: string;
  evidence: string;
  guard: string;
  transition: string;
  stages: MissionFlowStage[];
}

const stageOrder: MissionStageId[] = ['OBSERVE', 'REASON', 'ASSIGN', 'EXECUTE', 'VERIFY'];

function latestActivity(snapshot: JarvisSnapshot): SelfActivityContract | undefined {
  return snapshot.selfActivity[0];
}

function resolveProject(snapshot: JarvisSnapshot, selectedProjectId?: string): JarvisSnapshot['projects'][number] | undefined {
  return snapshot.projects.find((project) => project.id === selectedProjectId)
    ?? snapshot.projects.find((project) => project.state === 'ACTIVE')
    ?? snapshot.projects[0];
}

function activeStage(snapshot: JarvisSnapshot, project: JarvisSnapshot['projects'][number] | undefined): MissionStageId {
  if (project?.state === 'COMPLETED') return 'VERIFY';
  const latest = latestActivity(snapshot);
  if (snapshot.mode === 'Thinking') return 'REASON';
  if (snapshot.mode === 'Learning') return 'VERIFY';
  if (snapshot.mode === 'Working') return latest?.kind === 'DELEGATING' ? 'ASSIGN' : 'EXECUTE';
  return 'OBSERVE';
}

function stageDetail(id: MissionStageId, snapshot: JarvisSnapshot, project: JarvisSnapshot['projects'][number] | undefined, assignedModelName: string, latest: SelfActivityContract | undefined): string {
  if (id === 'OBSERVE') return `${snapshot.currentFocus} · ${project?.state ?? snapshot.mode}`;
  if (id === 'REASON') return snapshot.mode === 'Thinking' ? (latest?.title ?? 'Evaluating context and constraints') : 'Available when reasoning is active';
  if (id === 'ASSIGN') return latest?.kind === 'DELEGATING' ? (latest.detail ?? `${assignedModelName} is receiving work`) : `${assignedModelName} · assignment lane ready`;
  if (id === 'EXECUTE') return project?.currentAction ?? snapshot.workRuntime.detail;
  return project?.state === 'COMPLETED' ? 'Project state reports completion' : latest?.detail ?? `Last state change · ${snapshot.lastStateChange}`;
}

export function deriveMissionFlowState(snapshot: JarvisSnapshot, selectedProjectId?: string): MissionFlowState {
  const latest = latestActivity(snapshot);
  const project = resolveProject(snapshot, selectedProjectId);
  const workspace = snapshot.workspaces.find((item) => item.id === project?.workspaceId);
  const assignedModel = snapshot.models.find((model) => model.state === 'ACTIVE') ?? snapshot.models[0];
  const current = activeStage(snapshot, project);
  const resourceGuard = snapshot.resources.pressure === 'HIGH' || snapshot.resources.strategy === 'LIMITED_CONCURRENCY';
  const attention = snapshot.attentionRequired || snapshot.mode === 'Needs You';
  const complete = project?.state === 'COMPLETED';
  const paused = project?.state === 'PAUSED' || snapshot.workRuntime.state === 'PAUSED';
  const waiting = project?.state === 'WAITING' || snapshot.mode === 'Waiting';

  const status: MissionFlowState['status'] = !snapshot.online
    ? 'OFFLINE'
    : attention
      ? 'ATTENTION'
      : complete
        ? 'COMPLETE'
        : paused || resourceGuard
          ? 'GUARDED'
          : waiting
            ? 'STANDBY'
            : 'ACTIVE';

  const stages = stageOrder.map((id) => ({
    id,
    label: id,
    detail: stageDetail(id, snapshot, project, assignedModel?.name ?? 'Standby', latest),
    status: id === current
      ? complete ? 'ACTIVE' : attention ? 'ATTENTION' : paused || resourceGuard ? 'GUARDED' : 'ACTIVE'
      : 'READY',
  }));

  const headline = status === 'OFFLINE'
    ? 'Core unavailable'
    : status === 'ATTENTION'
      ? 'Your attention is required'
      : status === 'COMPLETE'
        ? `${project?.name ?? 'Mission'} reports completion`
        : status === 'GUARDED'
          ? paused ? `${project?.name ?? 'Mission'} is paused` : 'Operating under resource guard'
          : status === 'STANDBY'
            ? 'Standing by for a meaningful transition'
            : `${current} is the current mission stage`;

  const evidence = latest?.title ?? project?.currentAction ?? snapshot.currentFocus;
  const guard = attention
    ? snapshot.attentionReason
    : paused
      ? `Runtime ${snapshot.workRuntime.state} · ${snapshot.workRuntime.detail}`
      : resourceGuard
        ? `${snapshot.resources.strategy} · ${snapshot.resources.activeModelTasks}/${snapshot.resources.concurrencyLimit} model task capacity`
        : complete
          ? 'Completion is reported by the selected project state'
          : `${assignedModel?.name ?? 'No active model'} · ${snapshot.workRuntime.state}`;
  const transition = complete ? 'No next transition required' : project?.currentAction ?? snapshot.workRuntime.detail;

  return {
    stage: current,
    status,
    projectId: project?.id,
    projectName: project?.name,
    workspaceName: workspace?.name,
    modelName: assignedModel?.name,
    headline,
    evidence,
    guard,
    transition,
    stages,
  };
}
