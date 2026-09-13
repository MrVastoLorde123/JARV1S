import unittest
from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceService
from src.runtime.autonomous_reasoning_run_loop import AutonomousReasoningRunLoop
from src.runtime.autonomous_runtime_scheduler import AutonomousRuntimeSchedule, AutonomousRuntimeScheduler

class Store:
    def __init__(self): self.jobs={}; self.schedule=None
    def save(self,v):
        if isinstance(v,AutonomousJob): self.jobs[v.job_id]=v
        else: self.schedule=v
        return "revision"
    def load(self,j): return self.jobs.get(j)
    def load_due(self,n): return [] if self.schedule is None or self.schedule.next_due>n else [self.schedule]
    def claim(self,schedule,now,lease_seconds):
        token="lease-1"
        self.schedule=AutonomousRuntimeSchedule(schedule.job_id,schedule.next_due,schedule.interval,claim_token=token,lease_until=now+lease_seconds)
        return token
    def complete_claim(self,schedule,token,replacement):
        if self.schedule is None or self.schedule.claim_token != token: return False
        self.schedule=replacement
        return True

class FailingRunLoop(AutonomousReasoningRunLoop):
    def __init__(self): pass
    def run(self,job_id,*,max_pulses=1): raise RuntimeError("worker crashed")

class M72SchedulerFailureRecoveryTests(unittest.TestCase):
    def build(self,store):
        AutonomousJobPersistenceService(store).persist(AutonomousJob("j72","inspect").start())
        return AutonomousRuntimeScheduler(store,FailingRunLoop())
    def test_failure_is_observable_and_released_into_retry(self):
        store=Store(); scheduler=self.build(store); scheduler.schedule("j72",next_due=1,interval=5)
        out=scheduler.tick(1)[0]
        self.assertIsNone(out.run); self.assertEqual(out.failure,"RuntimeError: worker crashed")
        self.assertTrue(out.completed_claim); self.assertFalse(out.removed)
        self.assertEqual(store.schedule.next_due,6); self.assertIsNone(store.schedule.claim_token)
    def test_failure_is_not_success(self):
        store=Store(); scheduler=self.build(store); scheduler.schedule("j72",next_due=1,interval=5)
        out=scheduler.tick(1)[0]
        self.assertIsNotNone(out.failure); self.assertIsNone(out.run); self.assertFalse(out.removed)

if __name__ == "__main__": unittest.main()
