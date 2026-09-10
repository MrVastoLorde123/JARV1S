import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import type { JarvisSnapshot } from './contracts';
import MissionFlow from './MissionFlow';
import MissionPipeline from './MissionPipeline';
import LiveMissionsFooter from './LiveMissionsFooter';

type Space = 'HOME' | 'CHAT' | 'WORK' | 'CONTROL' | 'MIND' | 'CAPABILITIES' | 'SELF';

interface MissionSpineProps {
  snapshot: JarvisSnapshot;
  selectedProjectId: string;
  selectedWorkspaceId: string;
  navigate: (space: Space) => void;
  onSelectProject: (id: string) => void;
  onSelectWorkspace: (id: string) => void;
}

function MissionSpine({
  snapshot,
  selectedProjectId,
  selectedWorkspaceId: _selectedWorkspaceId,
  navigate,
  onSelectProject,
  onSelectWorkspace: _onSelectWorkspace,
}: MissionSpineProps) {
  const [flowHost, setFlowHost] = useState<HTMLElement | null>(null);
  const [pipelineHost, setPipelineHost] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const state = document.body;
    state.dataset.jarvisState = snapshot.online ? 'ONLINE' : 'OFFLINE';
    state.dataset.jarvisPressure = snapshot.resources.pressure;
    state.dataset.jarvisAttention = String(snapshot.attentionRequired);
    state.dataset.jarvisMode = snapshot.mode.toLowerCase();
    return () => {
      delete state.dataset.jarvisState;
      delete state.dataset.jarvisPressure;
      delete state.dataset.jarvisAttention;
      delete state.dataset.jarvisMode;
    };
  }, [snapshot.online, snapshot.resources.pressure, snapshot.attentionRequired, snapshot.mode]);

  useEffect(() => {
    const syncHosts = () => {
      const flow = document.querySelector<HTMLElement>('.mission-flow');
      const pipeline = document.querySelector<HTMLElement>('.pipeline');
      setFlowHost((current) => current === flow ? current : flow);
      setPipelineHost((current) => current === pipeline ? current : pipeline);
    };
    syncHosts();
    const observer = new MutationObserver(syncHosts);
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, []);

  return (
    <>
      {flowHost ? createPortal(<MissionFlow snapshot={snapshot} selectedProjectId={selectedProjectId} />, flowHost) : null}
      {pipelineHost ? createPortal(<MissionPipeline snapshot={snapshot} selectedProjectId={selectedProjectId} />, pipelineHost) : null}
      {createPortal(
        <LiveMissionsFooter
          snapshot={snapshot}
          selectedProjectId={selectedProjectId}
          onSelectProject={onSelectProject}
          navigate={navigate}
        />,
        document.body,
      )}
    </>
  );
}

export default MissionSpine;
