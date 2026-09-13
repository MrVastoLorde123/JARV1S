import unittest

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.runtime.autonomous_reasoning_feedback_pulse import AutonomousReasoningFeedbackPulse
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_reasoning_tool_feedback_cycle import AutonomousReasoningToolFeedbackCycleCoordinator
from src.runtime.autonomous_reasoning_tool_gate import AutonomousReasoningToolGate
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeScheduler
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService

class Store:
    def __init__(self): self.jobs={}; self.schedule=None
    def save(self,x):
        if isinstance(x,AutonomousJob): self.jobs[x.job_id]=x
        else: self.schedule=x
        return "r"
    def load(self,j): return self.jobs.get(j)
    def load_due(self,n): return [] if self.schedule is None or self.schedule.next_due>n else [self.schedule]
    def delete(self,j): self.schedule=None

class M68SchedulerSmoke(unittest.TestCase):
    def build(self, action):
        store=Store(); persistence=AutonomousJobPersistenceService(store); persistence.persist(AutonomousJob("j68","inspect").start())
        gate=AutonomousReasoningToolGate(ToolRegistry(), ToolService(ToolRegistry()))
        worker=AutonomousReasoningWorker(lambda job: action)
        coordinator=AutonomousReasoningToolFeedbackCycleCoordinator(worker,gate)
        pulse=AutonomousReasoningFeedbackPulse(persistence,coordinator)
        return AutonomousRuntimeScheduler(store,AutonomousReasoningRunLoop(pulse)),store
    def test_due_terminal_removed(self):
        s,store=self.build(AutonomousReasoningAction("a",AutonomousReasoningDisposition.COMPLETE,"done",result="ok")); s.schedule("j68",next_due=1,interval=5); out=s.tick(1)[0]; self.assertEqual(out.run.job.status,AutonomousJobStatus.COMPLETED); self.assertTrue(out.removed); self.assertIsNone(store.schedule)
    def test_not_due_untouched(self):
        s,store=self.build(AutonomousReasoningAction("a",AutonomousReasoningDisposition.COMPLETE,"done",result="ok")); s.schedule("j68",next_due=2,interval=5); self.assertEqual(s.tick(1),()); self.assertIsNotNone(store.schedule)

if __name__ == "__main__": unittest.main()
