import unittest

from src.core.environment_evidence_current_context import EnvironmentCurrentContext
from src.core.environment_context_composition import (
    EnvironmentContextCompositionError,
    EnvironmentContextCompositionService,
    EnvironmentCurrentContextBundle,
)
from src.core.environment_observation_evidence_qualification import EvidenceQualification


class EnvironmentContextCompositionTests(unittest.TestCase):
    def make_context(
        self,
        *,
        context_id="ctx-hardware",
        domain="hardware",
        environment_id="env-1",
        evidence_status=EvidenceQualification.USABLE,
    ):
        return EnvironmentCurrentContext(
            context_id=context_id,
            environment_id=environment_id,
            domain=domain,
            subject_kind="observation",
            data={"observed": {domain: {"value": 1}}, "status": "qualified"},
            evidence_status=evidence_status,
            observation_ids=(f"obs-{domain}",),
            adapter_ids=(f"adapter-{domain}",),
            provenance_id=f"prov-{domain}",
            qualification_id=f"qual-{domain}",
            lineage={"source": domain},
        )

    def setUp(self):
        self.service = EnvironmentContextCompositionService()
        self.hardware = self.make_context()
        self.software = self.make_context(
            context_id="ctx-software",
            domain="software",
        )

    def test_single_context_can_form_bundle(self):
        result = self.service.compose((self.hardware,), bundle_id="bundle-1")
        self.assertIsInstance(result, EnvironmentCurrentContextBundle)
        self.assertTrue(result.usable_for_reasoning)
        self.assertEqual(result.represented_domains, ("hardware",))
        self.assertIn("software", result.missing_domains)
        self.assertEqual(result.context_ids, ("ctx-hardware",))

    def test_multiple_domains_are_composed_without_overwriting(self):
        result = self.service.compose(
            (self.hardware, self.software),
            bundle_id="bundle-2",
        )
        self.assertEqual(result.represented_domains, ("hardware", "software"))
        self.assertEqual(tuple(result.data_by_domain), ("hardware", "software"))
        self.assertEqual(result.data_by_domain["hardware"], self.hardware.data)
        self.assertEqual(result.data_by_domain["software"], self.software.data)
        self.assertEqual(result.qualification_ids, ("qual-hardware", "qual-software"))
        self.assertEqual(result.provenance_ids, ("prov-hardware", "prov-software"))

    def test_missing_domains_are_explicit_not_marked_unavailable(self):
        result = self.service.compose((self.hardware,), bundle_id="bundle-missing")
        self.assertEqual(
            set(result.represented_domains) | set(result.missing_domains),
            {
                "hardware", "software", "network", "models", "capabilities",
                "permissions", "performance", "costs", "resources", "metadata",
            },
        )
        self.assertNotIn("unavailable", result.missing_domains)

    def test_non_usable_context_is_rejected(self):
        stale = self.make_context(
            context_id="ctx-stale",
            evidence_status=EvidenceQualification.UNUSABLE,
        )
        with self.assertRaises(EnvironmentContextCompositionError):
            self.service.compose((stale,), bundle_id="bundle-bad")

    def test_mixed_environments_are_rejected(self):
        other = self.make_context(
            context_id="ctx-other",
            domain="software",
            environment_id="env-2",
        )
        with self.assertRaises(EnvironmentContextCompositionError):
            self.service.compose((self.hardware, other), bundle_id="bundle-mixed-env")

    def test_duplicate_domains_are_rejected(self):
        duplicate = self.make_context(context_id="ctx-hardware-2")
        with self.assertRaises(EnvironmentContextCompositionError):
            self.service.compose((self.hardware, duplicate), bundle_id="bundle-duplicate-domain")

    def test_duplicate_context_ids_are_rejected(self):
        duplicate = self.make_context(domain="software")
        duplicate = EnvironmentCurrentContext(
            context_id=self.hardware.context_id,
            environment_id=duplicate.environment_id,
            domain=duplicate.domain,
            subject_kind=duplicate.subject_kind,
            data=duplicate.data,
            evidence_status=duplicate.evidence_status,
            observation_ids=duplicate.observation_ids,
            adapter_ids=duplicate.adapter_ids,
            provenance_id=duplicate.provenance_id,
            qualification_id=duplicate.qualification_id,
            lineage=duplicate.lineage,
        )
        with self.assertRaises(EnvironmentContextCompositionError):
            self.service.compose((self.hardware, duplicate), bundle_id="bundle-duplicate-id")

    def test_lineage_is_immutable(self):
        result = self.service.compose(
            (self.hardware, self.software),
            bundle_id="bundle-lineage",
            lineage={"parent": {"kind": "environment-context"}},
        )
        self.assertEqual(result.lineage["parent"]["kind"], "environment-context")
        with self.assertRaises(TypeError):
            result.lineage["parent"]["kind"] = "changed"

    def test_data_is_immutable(self):
        result = self.service.compose((self.hardware,), bundle_id="bundle-data")
        with self.assertRaises(TypeError):
            result.data_by_domain["hardware"]["observed"]["hardware"]["value"] = 2

    def test_upstream_contexts_are_preserved(self):
        result = self.service.compose((self.hardware, self.software), bundle_id="bundle-preserve")
        self.assertIs(result.contexts[0], self.hardware)
        self.assertIs(result.contexts[1], self.software)
        self.assertEqual(result.contexts, (self.hardware, self.software))


if __name__ == "__main__":
    unittest.main()
