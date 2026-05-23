import re
from typing import Any, Dict

SUPPORTED_TASK_TYPES: frozenset = frozenset(
    {"general", "math", "finance", "spatial", "grid", "agentic"}
)


class ContextEngineeringAuditor:
    """
    A comprehensive Context Engineering evaluator that audits prompts against
    2026 cognitive architectures, security parameters, and token optimization
    protocols.
    """

    def __init__(self) -> None:
        self._structural_patterns: Dict[str, str] = {
            "objective_rubric": r"(?i)\b1-5 scoring\b|\bYes/No\b|\bstrict criteria\b",
            "system_isolation": r"(?i)<sandboxed_context>|<untrusted_data>",
        }

        # Tuple (immutable) to prevent accidental mutation.
        self._persona_fluff_flags: tuple = (
            "years old",
            "gender",
            "lives in",
            "married",
            "hobbies",
            "expert with",
            "years of experience",
        )

    def _evaluate_legacy_heuristics(self, prompt: str) -> Dict[str, Any]:
        """Flags obsolete heuristics that degrade reasoning-native models."""
        lower_prompt = prompt.lower()
        if "step-by-step" in lower_prompt or "step by step" in lower_prompt:
            return {
                "status": "Critical Warning",
                "advice": (
                    "Reasoning models already generate hidden internal thought traces. "
                    "Forcing them to 'think step by step' is redundant, slows down "
                    "response times, and interferes with native logic."
                ),
            }
        return {"status": "Optimal", "advice": "No legacy sequential heuristics detected."}

    def _evaluate_persona_inversion(self, prompt: str) -> Dict[str, Any]:
        """Evaluates persona robustness to prevent prompting inversion and hallucination."""
        lower_prompt = prompt.lower()
        fluff_found = [flag for flag in self._persona_fluff_flags if flag in lower_prompt]

        if fluff_found:
            advice = (
                "Assigning overly complex personas limits the model, degrading factual "
                "accuracy and amplifying bias. Role prompting should solely be used to "
                "enforce tone and output formatting."
            )
        else:
            advice = "Persona is structurally sound."

        return {
            "status": "Warning" if fluff_found else "Optimal",
            "fluff_detected": fluff_found,
            "advice": advice,
        }

    def _evaluate_cognitive_routing(self, prompt: str, task_type: str) -> Dict[str, str]:
        """Verifies if the correct advanced cognitive architecture is used for the task type."""
        lower_prompt = prompt.lower()

        if task_type in ("math", "finance"):
            if "python" not in lower_prompt and "execute" not in lower_prompt:
                return {
                    "status": "Sub-optimal Routing",
                    "advice": (
                        "For complex math, LLMs struggle with deterministic logic. Delegate "
                        "heavy lifting via Program of Thoughts (PoT) by prompting the model "
                        "to generate a structured Python script for an external interpreter."
                    ),
                }
        elif task_type in ("spatial", "grid"):
            # Match directional arrows or explicit grid-cell notation [x]/[X]/[ ].
            # Avoid matching the bare letter 'x' to prevent false positives on
            # common words like "context", "execute", or "example".
            if not re.search(r"[↑↓]|\[[ xX]\]", prompt):
                return {
                    "status": "Sub-optimal Routing",
                    "advice": (
                        "For spatial reasoning, traditional Chain-of-Thought is inefficient. "
                        "Use Chain-of-Symbol (CoS) utilizing symbols (like ↑, ↓, [x]) to "
                        "radically compress reasoning tokens."
                    ),
                }
        elif task_type == "agentic":
            if (
                "thought" not in lower_prompt
                or "action" not in lower_prompt
                or "observation" not in lower_prompt
            ):
                return {
                    "status": "Sub-optimal Routing",
                    "advice": (
                        "Agentic workflows require the ReAct (Reason + Act) loop schema to "
                        "ground the LLM in real-world data and allow dynamic error recovery."
                    ),
                }

        return {"status": "Optimal", "advice": f"Correct cognitive routing deployed for {task_type}."}

    def _evaluate_sycophancy_rubrics(self, prompt: str) -> Dict[str, str]:
        """Checks for rigid constraints to combat algorithmic sycophancy."""
        if not re.search(self._structural_patterns["objective_rubric"], prompt):
            return {
                "status": "Warning",
                "advice": (
                    "Lacks Objective Rubrics. To extract honest analysis and prevent the AI "
                    "from flattering you, use rigid 1-5 scoring criteria or strict Yes/No "
                    "constraints requiring one-sentence justifications."
                ),
            }
        return {"status": "Optimal", "advice": "Objective Rubrics detected."}

    def _evaluate_idpi_defenses(self, prompt: str) -> Dict[str, str]:
        """Audits prompt for system isolation against Indirect Prompt Injection."""
        if not re.search(self._structural_patterns["system_isolation"], prompt):
            return {
                "status": "Warning",
                "advice": (
                    "Missing System Prompt Isolation. Attackers hide malicious instructions "
                    "inside untrusted documents. Implement a sandboxed dual-model architecture "
                    "for untrusted data."
                ),
            }
        return {"status": "Optimal", "advice": "System Isolation tags detected."}

    def run_master_audit(self, draft_prompt: str, task_type: str = "general") -> str:
        """
        Executes the holistic 2026 prompt audit pipeline.

        Args:
            draft_prompt: The prompt text to audit. Must be a non-empty string.
            task_type: One of "general", "math", "finance", "spatial", "grid",
                       or "agentic". Defaults to "general".

        Returns:
            A formatted Markdown report string.

        Raises:
            ValueError: If draft_prompt is empty or task_type is not supported.
        """
        if not isinstance(draft_prompt, str) or not draft_prompt.strip():
            raise ValueError("draft_prompt must be a non-empty string.")
        if task_type not in SUPPORTED_TASK_TYPES:
            raise ValueError(
                f"Unsupported task_type '{task_type}'. "
                f"Choose from: {sorted(SUPPORTED_TASK_TYPES)}"
            )

        legacy_eval = self._evaluate_legacy_heuristics(draft_prompt)
        persona_eval = self._evaluate_persona_inversion(draft_prompt)
        routing_eval = self._evaluate_cognitive_routing(draft_prompt, task_type)
        sycophancy_eval = self._evaluate_sycophancy_rubrics(draft_prompt)
        security_eval = self._evaluate_idpi_defenses(draft_prompt)

        report = [
            "## Unified Context Engineering Engine: Master Audit\n",
            f"**1. Legacy Heuristics Check:** {legacy_eval['status']}",
            f"   - *Diagnostic:* {legacy_eval['advice']}\n",
            f"**2. Prompting Inversion Check:** {persona_eval['status']}",
        ]
        if persona_eval["fluff_detected"]:
            report.append(f"   - *Flags:* {', '.join(persona_eval['fluff_detected'])}")
        report += [
            f"   - *Diagnostic:* {persona_eval['advice']}\n",
            f"**3. Cognitive Architecture Routing ({task_type.upper()}):** {routing_eval['status']}",
            f"   - *Diagnostic:* {routing_eval['advice']}\n",
            f"**4. Anti-Sycophancy Protocol:** {sycophancy_eval['status']}",
            f"   - *Diagnostic:* {sycophancy_eval['advice']}\n",
            f"**5. IDPI Security Layer:** {security_eval['status']}",
            f"   - *Diagnostic:* {security_eval['advice']}\n",
            "---\n*Audit Complete. Strict compliance is required prior to DSPy compiler execution.*",
        ]

        return "\n".join(report)


# ==========================================
# Execution Example
# ==========================================
if __name__ == "__main__":
    auditor = ContextEngineeringAuditor()

    flawed_prompt = """
    You are an expert mathematician with 20 years of experience.
    Think step-by-step to calculate the 50th Fibonacci number.
    Is my approach to this math problem good?
    """

    print(auditor.run_master_audit(flawed_prompt, task_type="math"))
