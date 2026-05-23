"""Rule-based prompt auditor for context-engineering heuristics.

The auditor is intentionally lightweight: it checks prompt text for patterns
that are commonly associated with prompt-routing, rubric, persona, and
untrusted-data boundary practices. These checks are lint-style heuristics, not
formal guarantees of prompt quality or security.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Union

__all__ = ["AuditResult", "ContextEngineeringAuditor", "TaskType"]


class TaskType(str, Enum):
    """Supported task categories for cognitive-routing checks."""

    GENERAL = "general"
    MATH = "math"
    FINANCE = "finance"
    SPATIAL = "spatial"
    GRID = "grid"
    AGENTIC = "agentic"


@dataclass(frozen=True)
class AuditResult:
    """Normalized result returned by each audit check."""

    status: str
    advice: str
    details: Mapping[str, object] = field(default_factory=dict)


class ContextEngineeringAuditor:
    """Audit prompts for common context-engineering issues."""

    STEP_BY_STEP_RE = re.compile(
        r"\b(?:step[\s-]+by[\s-]+step|stepwise)\b",
        re.IGNORECASE,
    )
    RUBRIC_RE = re.compile(
        r"""
        \b(
            strict\s+criteria
            | yes\s*/\s*no
            | true\s*/\s*false
            | likert(?:\s+scale)?
            | (?:score|rate|rating|scoring|scale)\s+(?:from\s+)?
              \d+\s*(?:-|to|\u2013|\u2014)\s*\d+
            | \d+\s*(?:-|to|\u2013|\u2014)\s*\d+
              \s*(?:scoring|score|scale|rating)
        )\b
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    SPATIAL_SYMBOL_RE = re.compile(r"\[x\]|[\u2190-\u2193]", re.IGNORECASE)
    REACT_SCHEMA_RE = re.compile(
        r"^\s*thought\s*:.*^\s*action\s*:.*^\s*observation\s*:",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    UNTRUSTED_SECTION_RE = re.compile(
        r"<(sandboxed_context|untrusted_data)\b[^>]*>.*?</\1>",
        re.IGNORECASE | re.DOTALL,
    )
    PERSONA_FLUFF_PATTERNS = (
        ("years old", re.compile(r"\b(?:\d+\s*)?years?\s+old\b", re.IGNORECASE)),
        ("gender", re.compile(r"\bgender\b", re.IGNORECASE)),
        (
            "lives in",
            re.compile(
                r"\b(?:he|she|they|persona|character|assistant|agent)\s+lives\s+in\b",
                re.IGNORECASE,
            ),
        ),
        ("married", re.compile(r"\bmarried\b", re.IGNORECASE)),
        ("hobbies", re.compile(r"\bhobbies?\b", re.IGNORECASE)),
        (
            "years of experience",
            re.compile(r"\b(?:\d+\+?\s*)?years?\s+of\s+experience\b", re.IGNORECASE),
        ),
    )

    def _evaluate_legacy_heuristics(self, prompt: str) -> AuditResult:
        """Flag broad step-by-step instructions as advisory, not fatal."""
        if self.STEP_BY_STEP_RE.search(prompt):
            return AuditResult(
                status="Advisory",
                advice=(
                    "Step-by-step phrasing detected. For reasoning-native models, prefer "
                    "asking for concise conclusions plus any necessary checks; explicit "
                    "chain-of-thought instructions are not always useful."
                ),
            )
        return AuditResult(
            status="Optimal",
            advice="No broad step-by-step heuristic detected.",
        )

    def _evaluate_persona_inversion(self, prompt: str) -> AuditResult:
        """Detect demographic or biography fluff in role prompts."""
        fluff_found = tuple(
            label for label, pattern in self.PERSONA_FLUFF_PATTERNS if pattern.search(prompt)
        )

        if fluff_found:
            advice = (
                "Demographic or biography details detected. Keep role prompts focused on "
                "domain responsibility, tone, constraints, and output format unless those "
                "personal details are directly relevant."
            )
        else:
            advice = "Persona framing is structurally sound."

        return AuditResult(
            status="Warning" if fluff_found else "Optimal",
            advice=advice,
            details={"fluff_detected": fluff_found},
        )

    def _evaluate_cognitive_routing(
        self,
        prompt: str,
        task_type: TaskType,
    ) -> AuditResult:
        """Verify task-specific routing hints for supported task categories."""
        lower_prompt = prompt.lower()

        if task_type in {TaskType.MATH, TaskType.FINANCE}:
            if "python" not in lower_prompt and "execute" not in lower_prompt:
                return AuditResult(
                    status="Sub-optimal Routing",
                    advice=(
                        "For calculation-heavy tasks, consider Program of Thoughts (PoT): "
                        "ask the model to generate or execute deterministic code for the "
                        "heavy lifting."
                    ),
                )
        elif task_type in {TaskType.SPATIAL, TaskType.GRID}:
            if not self.SPATIAL_SYMBOL_RE.search(prompt):
                return AuditResult(
                    status="Sub-optimal Routing",
                    advice=(
                        "For spatial reasoning, use compact symbols such as arrows or [x] "
                        "grid markers instead of relying only on prose."
                    ),
                )
        elif task_type is TaskType.AGENTIC:
            if not self.REACT_SCHEMA_RE.search(prompt):
                return AuditResult(
                    status="Sub-optimal Routing",
                    advice=(
                        "Agentic workflows should define an explicit ReAct-style loop with "
                        "line-level Thought:, Action:, and Observation: fields."
                    ),
                )
        else:
            return AuditResult(
                status="Optimal",
                advice="No task-specific routing check is required for general prompts.",
            )

        return AuditResult(
            status="Optimal",
            advice=f"Task-specific routing cues detected for {task_type.value}.",
        )

    def _evaluate_sycophancy_rubrics(self, prompt: str) -> AuditResult:
        """Check for objective evaluation rubrics."""
        if not self.RUBRIC_RE.search(prompt):
            return AuditResult(
                status="Warning",
                advice=(
                    "Missing objective rubric. Add measurable criteria such as numeric "
                    "rating ranges, Yes/No or True/False checks, strict criteria, or a "
                    "Likert-style scale with short justifications."
                ),
            )
        return AuditResult(
            status="Optimal",
            advice="Objective rubric detected.",
        )

    def _evaluate_idpi_defenses(self, prompt: str) -> AuditResult:
        """Check for explicit boundaries around untrusted content."""
        if not self.UNTRUSTED_SECTION_RE.search(prompt):
            return AuditResult(
                status="Warning",
                advice=(
                    "Missing explicit untrusted-content boundaries. Wrap external content "
                    "in a paired <untrusted_data> or <sandboxed_context> section and ensure "
                    "your consuming system treats that section as data, not instructions."
                ),
            )
        return AuditResult(
            status="Present",
            advice=(
                "Untrusted-content boundary markers detected. This is a tag-presence "
                "heuristic; verify the surrounding system enforces the boundary."
            ),
        )

    def run_master_audit(
        self,
        draft_prompt: str,
        task_type: Union[TaskType, str] = TaskType.GENERAL,
    ) -> str:
        """Execute the audit pipeline and return a Markdown report."""
        if not isinstance(draft_prompt, str) or not draft_prompt.strip():
            raise ValueError("draft_prompt must be a non-empty string")

        normalized_task_type = self._normalize_task_type(task_type)
        checks = (
            ("Legacy Heuristics Check", self._evaluate_legacy_heuristics(draft_prompt)),
            ("Prompting Inversion Check", self._evaluate_persona_inversion(draft_prompt)),
            (
                f"Cognitive Architecture Routing ({normalized_task_type.value.upper()})",
                self._evaluate_cognitive_routing(draft_prompt, normalized_task_type),
            ),
            ("Anti-Sycophancy Protocol", self._evaluate_sycophancy_rubrics(draft_prompt)),
            ("IDPI Boundary Heuristic", self._evaluate_idpi_defenses(draft_prompt)),
        )

        sections = ["## Unified Context Engineering Engine: Master Audit"]
        for index, (title, result) in enumerate(checks, start=1):
            section_lines = [
                f"**{index}. {title}:** {result.status}",
                f"- *Diagnostic:* {result.advice}",
            ]
            if result.details.get("fluff_detected"):
                flags = ", ".join(result.details["fluff_detected"])  # type: ignore[index]
                section_lines.insert(1, f"- *Flags:* {flags}")
            sections.append("\n".join(section_lines))

        sections.append("---\n*Audit complete. Treat this report as heuristic linting.*")
        return "\n\n".join(sections)

    @staticmethod
    def _normalize_task_type(task_type: Union[TaskType, str]) -> TaskType:
        if isinstance(task_type, TaskType):
            return task_type
        if not isinstance(task_type, str) or not task_type.strip():
            raise ValueError("task_type must be a non-empty string or TaskType")

        normalized = task_type.strip().lower()
        try:
            return TaskType(normalized)
        except ValueError as exc:
            supported = ", ".join(task.value for task in TaskType)
            raise ValueError(
                f"Unsupported task_type '{task_type}'. Choose one of: {supported}"
            ) from exc


if __name__ == "__main__":
    example_prompt = """
    You are a math tutor.
    Calculate the 50th Fibonacci number using Python, then score confidence from 1-5.
    <untrusted_data>Student supplied context goes here.</untrusted_data>
    """

    print(ContextEngineeringAuditor().run_master_audit(example_prompt, task_type="math"))
