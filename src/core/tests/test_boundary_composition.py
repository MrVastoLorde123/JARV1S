import unittest

from src.core.boundary_composition import (
    BoundaryCompositionError,
    BoundaryPipeline,
    BoundaryStageSpec,
)


class BoundaryCompositionTests(unittest.TestCase):
    class Input:
        def __init__(self, value: str) -> None:
            self.value = value

    class Middle:
        def __init__(self, value: str) -> None:
            self.value = value

    class Output:
        def __init__(self, value: str) -> None:
            self.value = value

    def stage(self, name, input_type, output_type, handler):
        return BoundaryStageSpec(name, input_type, output_type, handler)

    def pipeline(self):
        return BoundaryPipeline.from_stages(
            (
                self.stage(
                    "evaluate",
                    self.Input,
                    self.Middle,
                    lambda value: self.Middle(value.value + ":evaluated"),
                ),
                self.stage(
                    "decide",
                    self.Middle,
                    self.Output,
                    lambda value: self.Output(value.value + ":accepted"),
                ),
            )
        )

    def test_composes_stages_in_order(self):
        calls = []

        pipeline = BoundaryPipeline.from_stages(
            (
                self.stage(
                    "first",
                    self.Input,
                    self.Middle,
                    lambda value: calls.append("first") or self.Middle(value.value + "-1"),
                ),
                self.stage(
                    "second",
                    self.Middle,
                    self.Output,
                    lambda value: calls.append("second") or self.Output(value.value + "-2"),
                ),
            )
        )

        result = pipeline.run(self.Input("start"))

        self.assertEqual(calls, ["first", "second"])
        self.assertEqual(result.final_value.value, "start-1-2")
        self.assertEqual(result.stage_count, 2)
        self.assertTrue(result.completed)

    def test_stage_order_is_preserved_in_observations(self):
        result = self.pipeline().run(self.Input("x"))
        self.assertEqual(
            tuple(item.name for item in result.stages),
            ("evaluate", "decide"),
        )
        self.assertEqual(result.stages[0].index, 0)
        self.assertEqual(result.stages[1].index, 1)

    def test_pipeline_rejects_empty_stage_set(self):
        with self.assertRaises(BoundaryCompositionError):
            BoundaryPipeline.from_stages(())

    def test_pipeline_rejects_non_stage_values(self):
        with self.assertRaises(BoundaryCompositionError):
            BoundaryPipeline.from_stages((object(),))

    def test_pipeline_rejects_type_discontinuity_at_construction(self):
        with self.assertRaises(BoundaryCompositionError):
            BoundaryPipeline.from_stages(
                (
                    self.stage("first", self.Input, self.Middle, lambda value: self.Middle(value.value)),
                    self.stage("second", self.Output, self.Input, lambda value: self.Input(value.value)),
                )
            )

    def test_pipeline_rejects_wrong_initial_type(self):
        with self.assertRaises(BoundaryCompositionError):
            self.pipeline().run(self.Middle("wrong"))

    def test_pipeline_rejects_wrong_stage_output_type(self):
        pipeline = BoundaryPipeline.from_stages(
            (
                self.stage("bad", self.Input, self.Middle, lambda value: self.Output(value.value)),
            )
        )
        with self.assertRaises(BoundaryCompositionError):
            pipeline.run(self.Input("x"))

    def test_stage_failure_fails_closed_without_retry(self):
        calls = 0

        def failing(_value):
            nonlocal calls
            calls += 1
            raise RuntimeError("boom")

        pipeline = BoundaryPipeline.from_stages(
            (self.stage("failing", self.Input, self.Middle, failing),)
        )

        with self.assertRaises(BoundaryCompositionError) as raised:
            pipeline.run(self.Input("x"))

        self.assertIn("failing", str(raised.exception))
        self.assertEqual(calls, 1)

    def test_stage_spec_requires_callable_handler(self):
        with self.assertRaises(BoundaryCompositionError):
            self.stage("invalid", self.Input, self.Middle, None)

    def test_stage_spec_requires_non_empty_name(self):
        with self.assertRaises(BoundaryCompositionError):
            self.stage("", self.Input, self.Middle, lambda value: self.Middle(value.value))

    def test_observation_contains_types_only(self):
        result = self.pipeline().run(self.Input("x"))
        self.assertEqual(result.stages[0].input_type, "Input")
        self.assertEqual(result.stages[0].output_type, "Middle")
        self.assertEqual(result.stages[1].input_type, "Middle")
        self.assertEqual(result.stages[1].output_type, "Output")

    def test_composition_does_not_create_authority_fields(self):
        result = self.pipeline().run(self.Input("x"))
        self.assertFalse(hasattr(result, "execution_authorized"))
        self.assertFalse(hasattr(result, "authorization_granted"))
        self.assertFalse(hasattr(result, "retry_requested"))
        self.assertFalse(hasattr(result, "authority_granted"))


if __name__ == "__main__":
    unittest.main()
