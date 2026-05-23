import unittest

from context_engineering_auditor import ContextEngineeringAuditor, TaskType


class ContextEngineeringAuditorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.auditor = ContextEngineeringAuditor()

    def test_empty_prompt_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "draft_prompt"):
            self.auditor.run_master_audit("")

        with self.assertRaisesRegex(ValueError, "draft_prompt"):
            self.auditor.run_master_audit(None)  # type: ignore[arg-type]

    def test_unknown_task_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported task_type"):
            self.auditor.run_master_audit("Review this prompt.", task_type="coding")

    def test_task_type_is_normalized(self) -> None:
        report = self.auditor.run_master_audit(
            "Use Python to calculate the answer. Score confidence from 1-5.",
            task_type=" Math ",
        )

        self.assertIn("Cognitive Architecture Routing (MATH)", report)
        self.assertIn("Task-specific routing cues detected for math", report)

    def test_spatial_check_does_not_match_bare_x_in_words(self) -> None:
        result = self.auditor._evaluate_cognitive_routing(
            "Use this example text to describe the grid.",
            TaskType.SPATIAL,
        )

        self.assertEqual(result.status, "Sub-optimal Routing")

    def test_spatial_check_accepts_grid_marker(self) -> None:
        result = self.auditor._evaluate_cognitive_routing(
            "Move from [x] to the next cell.",
            TaskType.GRID,
        )

        self.assertEqual(result.status, "Optimal")

    def test_persona_matching_uses_boundaries_and_context(self) -> None:
        result = self.auditor._evaluate_persona_inversion(
            "Build an agenda and consult an expert with the latest data. "
            "The service lives in production.",
        )

        self.assertEqual(result.status, "Optimal")
        self.assertEqual(result.details["fluff_detected"], ())

    def test_persona_matching_flags_demographic_fluff(self) -> None:
        result = self.auditor._evaluate_persona_inversion(
            "You are a persona who is 43 years old and married.",
        )

        self.assertEqual(result.status, "Warning")
        self.assertEqual(result.details["fluff_detected"], ("years old", "married"))

    def test_step_by_step_variants_are_detected(self) -> None:
        result = self.auditor._evaluate_legacy_heuristics("Think step\nby\nstep.")

        self.assertEqual(result.status, "Advisory")

    def test_rubric_variants_are_detected(self) -> None:
        for prompt in (
            "Rate from 1 to 10 with one-sentence justification.",
            "Use a true/false answer and explain briefly.",
            "Judge this on a Likert scale.",
        ):
            with self.subTest(prompt=prompt):
                result = self.auditor._evaluate_sycophancy_rubrics(prompt)
                self.assertEqual(result.status, "Optimal")

    def test_idpi_check_requires_paired_boundary(self) -> None:
        bare_tag = self.auditor._evaluate_idpi_defenses("Read <untrusted_data> input.")
        paired_tag = self.auditor._evaluate_idpi_defenses(
            "Read <untrusted_data> input </untrusted_data>."
        )

        self.assertEqual(bare_tag.status, "Warning")
        self.assertEqual(paired_tag.status, "Present")

    def test_agentic_check_requires_line_level_react_schema(self) -> None:
        loose_words = self.auditor._evaluate_cognitive_routing(
            "Thought, action, and observation are important.",
            TaskType.AGENTIC,
        )
        schema = self.auditor._evaluate_cognitive_routing(
            "Thought: inspect\nAction: search\nObservation: found result",
            TaskType.AGENTIC,
        )

        self.assertEqual(loose_words.status, "Sub-optimal Routing")
        self.assertEqual(schema.status, "Optimal")


if __name__ == "__main__":
    unittest.main()
