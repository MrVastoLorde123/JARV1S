import json
import unittest

from src.context.cross_domain import (
    CrossDomainContext,
    CrossDomainContextValidationError,
    CrossDomainLink,
    DomainReference,
)
from src.context.goal_project import GoalProjectContext, GoalStatus, GoalContext
from src.context.situational import SituationSignal, SituationalContext
from src.context.world_state import ContextState


class CrossDomainContextTests(unittest.TestCase):
    def setUp(self):
        self.state = ContextState(
            context_id="ctx-1",
            state={"location": "work", "activity": "engineering"},
            source_refs=("sensor:1",),
            observed_at="2026-09-03T14:00:00+00:00",
        )
        goal = GoalContext(goal_id="goal-1", name="Finish integration", status=GoalStatus.ACTIVE)
        self.goal_project = GoalProjectContext(goals=(goal,))
        self.situational = SituationalContext(
            context=self.state,
            signals=(SituationSignal(signal_id="s-1", category="activity", value="coding"),),
        )
        self.person = DomainReference("people", "person-1", "User")
        self.project = DomainReference("projects", "project-1", "JARVIS")
        self.link = CrossDomainLink(self.person, self.project, "works_on", ("memory:1",))

    def test_empty_context_is_valid(self):
        self.assertEqual(CrossDomainContext().references, ())

    def test_composes_existing_context_domains(self):
        context = CrossDomainContext(self.state, self.goal_project, self.situational)
        self.assertIs(context.context_state, self.state)
        self.assertIs(context.goal_project, self.goal_project)
        self.assertIs(context.situational, self.situational)

    def test_reference_is_immutable_and_bounded(self):
        ref = DomainReference("people", "person-1", metadata={"role": "engineer"})
        with self.assertRaises(TypeError):
            ref.metadata["role"] = "admin"

    def test_duplicate_domain_reference_rejected(self):
        with self.assertRaises(CrossDomainContextValidationError):
            CrossDomainContext(references=(self.person, DomainReference("PEOPLE", "person-1")))

    def test_domain_lookup_is_case_insensitive(self):
        context = CrossDomainContext(references=(self.person, self.project))
        self.assertEqual(context.references_for_domain("PEOPLE"), (self.person,))

    def test_link_requires_references(self):
        with self.assertRaises(CrossDomainContextValidationError):
            CrossDomainContext(links=(self.link,))

    def test_link_must_reference_known_endpoints(self):
        context = CrossDomainContext(references=(self.person,))
        unknown = CrossDomainLink(self.person, self.project, "works_on")
        with self.assertRaises(CrossDomainContextValidationError):
            context.with_link(unknown)

    def test_with_reference_is_functional(self):
        context = CrossDomainContext(references=(self.person,))
        updated = context.with_reference(self.project)
        self.assertEqual(len(context.references), 1)
        self.assertEqual(len(updated.references), 2)

    def test_with_link_is_functional(self):
        context = CrossDomainContext(references=(self.person, self.project))
        updated = context.with_link(self.link)
        self.assertEqual(context.links, ())
        self.assertEqual(updated.links, (self.link,))

    def test_links_for_matches_either_endpoint(self):
        context = CrossDomainContext(references=(self.person, self.project), links=(self.link,))
        self.assertEqual(context.links_for(self.person), (self.link,))
        self.assertEqual(context.links_for(self.project), (self.link,))

    def test_link_source_refs_are_bounded_and_unique(self):
        with self.assertRaises(CrossDomainContextValidationError):
            CrossDomainLink(self.person, self.project, "works_on", ("x", "x"))
        with self.assertRaises(CrossDomainContextValidationError):
            CrossDomainLink(self.person, self.project, "works_on", tuple(f"r-{i}" for i in range(257)))

    def test_serialization_contains_no_authority(self):
        context = CrossDomainContext(
            context_state=self.state,
            goal_project=self.goal_project,
            situational=self.situational,
            references=(self.person, self.project),
            links=(self.link,),
        )
        payload = context.to_dict()
        self.assertFalse(payload["truth_guaranteed"])
        self.assertFalse(payload["intent_guaranteed"])
        self.assertFalse(payload["authorization_granted"])
        self.assertFalse(payload["policy_authority"])
        self.assertFalse(payload["execution_requested"])
        json.loads(context.to_json())

    def test_metadata_is_frozen_recursively(self):
        ref = DomainReference("systems", "sys-1", metadata={"nested": {"mode": "safe"}})
        with self.assertRaises(TypeError):
            ref.metadata["nested"]["mode"] = "execute"

    def test_invalid_domain_reference_type(self):
        with self.assertRaises(TypeError):
            CrossDomainContext().with_reference("not-a-reference")

    def test_invalid_link_type(self):
        with self.assertRaises(TypeError):
            CrossDomainContext().with_link("not-a-link")

    def test_duplicate_link_rejected(self):
        context = CrossDomainContext(references=(self.person, self.project), links=(self.link,))
        with self.assertRaises(CrossDomainContextValidationError):
            context.with_link(self.link)

    def test_mixed_domains_can_be_composed_without_inference(self):
        device = DomainReference("systems", "hvac-1")
        location = DomainReference("locations", "site-1")
        link = CrossDomainLink(device, location, "located_at", ("event:9",))
        context = CrossDomainContext(references=(self.person, self.project, device, location), links=(self.link, link))
        self.assertEqual(len(context.references_for_domain("systems")), 1)
        self.assertEqual(len(context.links), 2)


if __name__ == "__main__":
    unittest.main()
