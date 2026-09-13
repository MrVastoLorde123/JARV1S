import unittest
from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition
from src.runtime.autonomous_reasoning_worker import AutonomousReasoningWorker
class M59Tests(unittest.TestCase):
 def j(self): return AutonomousJob('j1','goal')
 def a(self,d,**x): return {'action_id':'a1','disposition':d,'rationale':'r',**x}
 def test_continue(self): self.assertEqual(AutonomousReasoningWorker(lambda j:self.a('continue')).run_cycle(self.j()).disposition,AutonomousCycleDisposition.CONTINUE)
 def test_tool(self):
  r=AutonomousReasoningWorker(lambda j:self.a('tool_request',tool_name='ping')).run_cycle(self.j()); self.assertEqual(r.disposition,AutonomousCycleDisposition.WAIT_TOOL); self.assertIn('pending_tool_request',r.context_delta)
 def test_complete(self):
  r=AutonomousReasoningWorker(lambda j:self.a('complete',result='done')).run_cycle(self.j()); self.assertEqual(r.result,'done')
 def test_bad(self):
  r=AutonomousReasoningWorker(lambda j:object()).run_cycle(self.j()); self.assertEqual(r.disposition,AutonomousCycleDisposition.FAIL)
if __name__=='__main__': unittest.main()
