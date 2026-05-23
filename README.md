# Prompting-Engineer-2
import re
from typing import Dict, Any, List, Optional

class ContextEngineeringAuditor:
    """
    A comprehensive Context Engineering evaluator that audits prompts against 
    2026 cognitive architectures, security parameters, and token optimization protocols.
    """
    
    def __init__(self):
        # Enforces structured programmatic inputs over prose
        self.structural_patterns = {
            "declarative_signature": r"Context, .* -> .*",
            "objective_rubric": r"(?i)\b1-5 scoring\b|\bYes/No\b|\bstrict criteria\b",
            "modality_order": r"(?i)<image>|<audio>.*<text>",
            "system_isolation": r"(?i)<sandboxed_context>|<untrusted_data>"
        }
        
        # Flags legacy demographics and overly complex personas that amplify bias
        self.persona_fluff_flags = [
            "years old", "gender", "lives in", "married", "hobbies",
            "expert with", "years of experience"
        ]

    def _evaluate_legacy_heuristics(self, prompt: str) -> Dict[str, Any]:
        """Flags obsolete heuristics that degrade reasoning-native models."""
        lower_prompt = prompt.lower()
        if "step-by-step" in lower_prompt or "step by step" in lower_prompt:
            return {
                "status": "Critical Warning",
                "advice": "Reasoning models already generate hidden internal thought traces. Forcing them to 'think step by step' is redundant, slows down response times, and interferes with native logic."
            }
        return {"status": "Optimal", "advice": "No legacy sequential heuristics detected."}

    def _evaluate_persona_inversion(self, prompt: str) -> Dict[str, Any]:
        """Evaluates persona robustness to prevent prompting inversion and hallucination."""
        lower_prompt = prompt.lower()
        fluff_found = [flag for flag in self.persona_fluff_flags if flag in lower_prompt]
        
        advice = "Persona is structurally sound."
        if fluff_found:
            advice = "Assigning overly complex personas limits the model, degrading factual accuracy and amplifying bias. Role prompting should solely be used to enforce tone and output formatting."
            
        return {
            "status": "Warning" if fluff_found else "Optimal",
            "fluff_detected": fluff_found,
            "advice": advice
        }

    def _evaluate_cognitive_routing(self, prompt: str, task_type: str) -> Dict[str, str]:
        """Verifies if the correct advanced cognitive architecture is utilized based on task type."""
        lower_prompt = prompt.lower()
        
        if task_type == "math" or task_type == "finance":
            if "python" not in lower_prompt and "execute" not in lower_prompt:
                return {
                    "status": "Sub-optimal Routing",
                    "advice": "For complex math, LLMs struggle with deterministic logic. Delegate heavy lifting via Program of Thoughts (PoT) by prompting the model to generate a structured Python script for an external interpreter."
                }
        elif task_type == "spatial" or task_type == "grid":
            if not re.search(r"[↑↓\[\]x]", prompt):
                return {
                    "status": "Sub-optimal Routing",
                    "advice": "For spatial reasoning, traditional Chain-of-Thought is inefficient. Use Chain-of-Symbol (CoS) utilizing symbols (like ↑, ↓, [x]) to radically compress reasoning tokens."
                }
        elif task_type == "agentic":
            if "thought" not in lower_prompt or "action" not in lower_prompt or "observation" not in lower_prompt:
                return {
                    "status": "Sub-optimal Routing",
                    "advice": "Agentic workflows require the ReAct (Reason + Act) loop schema to ground the LLM in real-world data and allow dynamic error recovery."
                }
                
        return {"status": "Optimal", "advice": f"Correct cognitive routing deployed for {task_type}."}

    def _evaluate_sycophancy_rubrics(self, prompt: str) -> str:
        """Checks for rigid constraints to combat algorithmic sycophancy."""
        if not re.search(self.structural_patterns["objective_rubric"], prompt):
            return "Warning: Lacks Objective Rubrics. To extract honest analysis and prevent the AI from flattering you, use rigid 1-5 scoring criteria or strict Yes/No constraints requiring one-sentence justifications."
        return "Optimal: Objective Rubrics detected."

    def _evaluate_idpi_defenses(self, prompt: str) -> str:
        """Audits prompt for system isolation against Indirect Prompt Injection."""
        if not re.search(self.structural_patterns["system_isolation"], prompt):
            return "Warning: Missing System Prompt Isolation. Attackers hide malicious instructions inside untrusted documents. Implement a sandboxed dual-model architecture for untrusted data."
        return "Optimal: System Isolation tags detected."

    def run_master_audit(self, draft_prompt: str, task_type: str = "general") -> str:
        """Executes the holistic 2026 prompt audit pipeline."""
        
        # Execute sub-routines
        legacy_eval = self._evaluate_legacy_heuristics(draft_prompt)
        persona_eval = self._evaluate_persona_inversion(draft_prompt)
        routing_eval = self._evaluate_cognitive_routing(draft_prompt, task_type)
        sycophancy_eval = self._evaluate_sycophancy_rubrics(draft_prompt)
        security_eval = self._evaluate_idpi_defenses(draft_prompt)
        
        # Compile Report
        report = []
        report.append("## 🔬 Unified Context Engineering Engine: Master Audit\n")
        
        report.append(f"**1. Legacy Heuristics Check:** {legacy_eval['status']}")
        report.append(f"   - *Diagnostic:* {legacy_eval['advice']}\n")
        
        report.append(f"**2. Prompting Inversion Check:** {persona_eval['status']}")
        if persona_eval['fluff_detected']:
            report.append(f"   - *Flags:* {', '.join(persona_eval['fluff_detected'])}")
        report.append(f"   - *Diagnostic:* {persona_eval['advice']}\n")
        
        report.append(f"**3. Cognitive Architecture Routing ({task_type.upper()}):** {routing_eval['status']}")
        report.append(f"   - *Diagnostic:* {routing_eval['advice']}\n")
        
        report.append(f"**4. Anti-Sycophancy Protocol:**")
        report.append(f"   - *Diagnostic:* {sycophancy_eval}\n")
        
        report.append(f"**5. IDPI Security Layer:**")
        report.append(f"   - *Diagnostic:* {security_eval}\n")
        
        report.append("---\n*Audit Complete. Strict compliance is required prior to DSPy compiler execution.*")
        
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
