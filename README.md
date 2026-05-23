# Prompting-Engineer-2

A rule-based **Context Engineering Auditor** that lints LLM prompts against 2026
best practices covering cognitive architecture routing, anti-sycophancy rubrics,
persona hygiene, and Indirect Prompt Injection (IDPI) defences.

## Quick start

```bash
python context_engineering_auditor.py
```

Or import the class directly:

```python
from context_engineering_auditor import ContextEngineeringAuditor

auditor = ContextEngineeringAuditor()
report = auditor.run_master_audit(my_prompt, task_type="math")
print(report)
```

## Supported `task_type` values

| Value | Routing check applied |
|-------|-----------------------|
| `general` | No routing check |
| `math` | Program of Thoughts (PoT) — expects `python` or `execute` keyword |
| `finance` | Same as `math` |
| `spatial` | Chain-of-Symbol (CoS) — expects `↑`/`↓` or `[x]` grid markers |
| `grid` | Same as `spatial` |
| `agentic` | ReAct loop — expects `thought`, `action`, and `observation` keywords |

Passing an unsupported value raises `ValueError`.

## Audit pipeline

| # | Check | What it looks for |
|---|-------|-------------------|
| 1 | Legacy Heuristics | `step-by-step` / `step by step` instructions |
| 2 | Persona Inversion | Demographic or experience fluff in personas |
| 3 | Cognitive Routing | Correct reasoning architecture for the `task_type` |
| 4 | Anti-Sycophancy | Objective scoring rubrics (`1-5 scoring`, `Yes/No`, `strict criteria`) |
| 5 | IDPI Security | System-isolation tags (`<sandboxed_context>`, `<untrusted_data>`) |

## Requirements

Python ≥ 3.9, no third-party dependencies.
