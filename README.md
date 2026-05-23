# Prompting-Engineer-2

Prompting-Engineer-2 provides a small, dependency-free Python auditor for
linting prompts against context-engineering heuristics. It checks for common
prompt issues around:

- broad step-by-step instructions;
- demographic or biography-heavy persona prompts;
- task-specific routing cues for math, finance, spatial, grid, and agentic
  prompts;
- objective evaluation rubrics; and
- explicit boundaries around untrusted external content.

These checks are heuristics. They are useful as prompt linting signals, but
they do not prove prompt quality or guarantee security.

## Quick start

Run the demo:

```bash
python context_engineering_auditor.py
```

Or import the auditor:

```python
from context_engineering_auditor import ContextEngineeringAuditor

auditor = ContextEngineeringAuditor()
report = auditor.run_master_audit(
    """
    You are a math tutor.
    Calculate the 50th Fibonacci number using Python.
    Score confidence from 1-5 and justify the score in one sentence.
    <untrusted_data>Student supplied context goes here.</untrusted_data>
    """,
    task_type="math",
)
print(report)
```

## Supported task types

| Value | Routing check |
| --- | --- |
| `general` | No task-specific routing check |
| `math` | Looks for deterministic execution cues such as `python` or `execute` |
| `finance` | Same as `math` |
| `spatial` | Looks for compact spatial symbols such as arrows or `[x]` |
| `grid` | Same as `spatial` |
| `agentic` | Looks for line-level `Thought:`, `Action:`, and `Observation:` fields |

Task type values are case-insensitive after trimming whitespace. Unsupported
values raise `ValueError` instead of silently returning an "Optimal" routing
result.

## Development

Run the test suite with the standard library:

```bash
python -m unittest
```

The project has no runtime third-party dependencies.
