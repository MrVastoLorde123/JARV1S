import unittest
from src.ai.models import AIResponse,AICapabilities
from src.ai.provider import AIProvider
from src.ai.service import AIService
from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_ai_reasoning_provider import AutonomousAIReasoningProvider
class P(AIProvider):
 def provider_name(self): return 'p'
 def capabilities(self): return AICapabilities(structured_output=True)
 def generate(self,r): self.r=r; return AIResponse('{"disposition":"continue","rationale":"ok"}','p','x')
class T(unittest.TestCase):
 def test_reason(self):
  p=P(); s=AIService(); s.register_provider(p); s.set_default_provider('p'); out=AutonomousAIReasoningProvider(s).reason(AutonomousJob('j','inspect ATS')); self.assertIn('disposition',out); self.assertEqual(p.r.context['job_id'],'j')
 def test_bad_job(self):
  with self.assertRaises(TypeError): AutonomousAIReasoningProvider(AIService()).reason('x')
