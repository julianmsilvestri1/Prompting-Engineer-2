# Code Review – `Prompting-Engineer-2`

Reviewer: Cursor cloud agent
Scope: the entire repository (single file: `README.md`, which contains a Python
class named `ContextEngineeringAuditor`).
Commit reviewed: `e334be8` ("Update README.md") on `main`.

> Severity legend: 🔴 critical · 🟠 high · 🟡 medium · 🔵 low / nit

---

## 1. Repository-level / structural issues

### 1.1 🟠 Python source lives inside `README.md`

The only file in the repo is `README.md`, but its contents are raw Python
source (with one stray markdown header on line 1: `# Prompting-Engineer-2`).
Consequences:

- The file cannot be executed (`python README.md` will fail because of the
  markdown header).
- GitHub renders the body as a single `<h1>` followed by an unformatted text
  blob — the code is not in a fenced ```` ```python ```` block, so syntax
  highlighting is lost and indentation is preserved only by accident.
- IDEs, linters, type-checkers and test runners cannot pick the file up.
- A true `README.md` (project description, install instructions, usage,
  license) is missing entirely.

**Fix:** move the class into `context_engineering_auditor.py` (or a package
layout such as `src/prompting_engineer/auditor.py`) and write a proper
`README.md` that describes the project.

### 1.2 🟡 No project scaffolding

There is no `pyproject.toml`, `requirements.txt`, `LICENSE`, `.gitignore`,
test directory, CI configuration, or linter/formatter config. For a project
whose stated purpose is to "audit" prompts, the absence of automated tests
is particularly notable — every behavioural claim below is unverified.

### 1.3 🔵 Single-commit history with no PR template

History shows only `Initial commit` and `Update README.md`. There is no
contributing guide or PR template. Low priority, but worth adding once the
project grows.

---

## 2. Bugs and logic errors

### 2.1 🔴 `modality_order` regex has wrong operator precedence

```14:18:README.md
        self.structural_patterns = {
            "declarative_signature": r"Context, .* -> .*",
            "objective_rubric": r"(?i)\b1-5 scoring\b|\bYes/No\b|\bstrict criteria\b",
            "modality_order": r"(?i)<image>|<audio>.*<text>",
            "system_isolation": r"(?i)<sandboxed_context>|<untrusted_data>"
        }
```

`r"(?i)<image>|<audio>.*<text>"` is parsed as `(<image>)` **OR**
`(<audio>.*<text>)`. The intent — "image, then audio, then text in order" —
requires grouping, e.g. `r"(?i)<image>.*<audio>.*<text>"` or three explicit
ordered checks. (It happens not to bite at runtime today only because the
pattern is never used; see 2.2.)

### 2.2 🟠 Dead patterns: `declarative_signature` and `modality_order` are never used

Both keys are defined in `self.structural_patterns` but never referenced
anywhere else. Either wire them into evaluators or delete them — leaving them
in place misleads readers about which checks actually run.

### 2.3 🔴 Spatial-reasoning check has a catastrophic regex character class

```61:66:README.md
        elif task_type == "spatial" or task_type == "grid":
            if not re.search(r"[↑↓\[\]x]", prompt):
                return {
                    "status": "Sub-optimal Routing",
                    "advice": "For spatial reasoning, traditional Chain-of-Thought is inefficient. Use Chain-of-Symbol (CoS) utilizing symbols (like ↑, ↓, [x]) to radically compress reasoning tokens."
                }
```

`[↑↓\[\]x]` is a character class that matches a **single** occurrence of
`↑`, `↓`, `[`, `]`, or the literal letter `x`. Any prompt that happens to
contain the letter `x` — e.g. words like `explain`, `extract`, `next`,
`example`, `execute`, `exit`, `text`, `box`, `axis` — silently passes the
spatial check as "Optimal". This is a high-rate false-negative. The intended
token is presumably `[x]` (a grid-cell marker), so the check should look for
that as a sequence, e.g. `re.search(r"\[x\]|[↑↓]", prompt, re.IGNORECASE)`.

### 2.4 🟠 `_evaluate_legacy_heuristics` misses common variants

```28:33:README.md
        lower_prompt = prompt.lower()
        if "step-by-step" in lower_prompt or "step by step" in lower_prompt:
```

This substring check fails on legitimate variants such as `"step\nby\nstep"`
(line-wrapped), `"step  by  step"` (double space), `"think stepwise"`, or
`"think carefully and step by step:"` once any non-ASCII whitespace is
involved. Use a normalized whitespace check or a regex:
`re.search(r"step[\s-]+by[\s-]+step", lower_prompt)`.

### 2.5 🟠 Persona-fluff matching uses raw substring `in`, producing false positives

```21:24:README.md
        self.persona_fluff_flags = [
            "years old", "gender", "lives in", "married", "hobbies",
            "expert with", "years of experience"
        ]
```

`"gender" in lower_prompt` matches `"agenda"`, `"engender"`, `"transgender"`,
`"genderless"`. `"lives in"` matches `"the service lives in production"`.
`"expert with"` matches benign instructions like `"consult an expert with
the latest data"`. Use word-boundary regex:

```python
flag_re = re.compile(r"\b(" + "|".join(map(re.escape, self.persona_fluff_flags)) + r")\b")
fluff_found = flag_re.findall(lower_prompt)
```

### 2.6 🟡 `objective_rubric` pattern is far too narrow

```16:16:README.md
            "objective_rubric": r"(?i)\b1-5 scoring\b|\bYes/No\b|\bstrict criteria\b",
```

Only matches the literal phrases `1-5 scoring`, `Yes/No`, or `strict
criteria`. Equally valid rubrics — `"rate from 1 to 10"`, `"score 0–100"`,
`"true/false"`, `"on a Likert scale"` — produce false-positive warnings.
Either expand the pattern significantly or replace it with a more semantic
check (e.g. detect a digits-dash-digits range followed by a noun like
`scale`/`score`/`rating`).

### 2.7 🟠 `_evaluate_idpi_defenses` is security theater

```82:86:README.md
    def _evaluate_idpi_defenses(self, prompt: str) -> str:
        """Audits prompt for system isolation against Indirect Prompt Injection."""
        if not re.search(self.structural_patterns["system_isolation"], prompt):
            return "Warning: Missing System Prompt Isolation. ..."
        return "Optimal: System Isolation tags detected."
```

The check simply scans for the literal tags `<sandboxed_context>` or
`<untrusted_data>`. The presence of these tags provides **no** actual
isolation; an attacker controlling the untrusted content can include the
same tags inside the payload and defeat the "check". The advice text claims
the prompt now has "sandboxing" — a misleading guarantee. Either rename the
check ("Tag-presence heuristic") and soften the advice, or implement real
boundary semantics (e.g. require the tags to wrap a specific delimited
section that is parsed structurally).

### 2.8 🟡 `_evaluate_cognitive_routing` falls through silently on unknown `task_type`

```51:74:README.md
    def _evaluate_cognitive_routing(self, prompt: str, task_type: str) -> Dict[str, str]:
        ...
        if task_type == "math" or task_type == "finance":
            ...
        elif task_type == "spatial" or task_type == "grid":
            ...
        elif task_type == "agentic":
            ...
        return {"status": "Optimal", "advice": f"Correct cognitive routing deployed for {task_type}."}
```

If the caller passes `"Math"` (wrong case), `"finance "` (stray space),
`"coding"`, or any string the function doesn't recognize, the result is
silently `Optimal` with a message claiming "Correct cognitive routing
deployed for coding." That message is false — no check was performed.

**Fix:** normalize input (`task_type = task_type.strip().lower()`), validate
against a known set, and either raise or return a distinct `"Unknown task
type"` status.

### 2.9 🟡 `task_type` should be an `Enum` / `Literal`, not a free-form `str`

Related to 2.8. Using `typing.Literal["math","finance","spatial","grid","agentic","general"]`
or an `enum.Enum` would let type-checkers catch typos at call sites.

### 2.10 🟡 `run_master_audit` has no input validation

```88:96:README.md
    def run_master_audit(self, draft_prompt: str, task_type: str = "general") -> str:
        """Executes the holistic 2026 prompt audit pipeline."""
        ...
        legacy_eval = self._evaluate_legacy_heuristics(draft_prompt)
```

Passing `None` produces an `AttributeError` deep inside
`_evaluate_legacy_heuristics` (`'NoneType' object has no attribute 'lower'`).
Passing an empty string passes every check (everything is "Optimal"), which
is technically a vulnerability of the audit pipeline itself — the auditor
claims a prompt with literally no content is well-engineered.

Add an explicit guard:

```python
if not isinstance(draft_prompt, str) or not draft_prompt.strip():
    raise ValueError("draft_prompt must be a non-empty string")
```

### 2.11 🔵 Inconsistent return shapes between evaluators

| Method | Returns |
| --- | --- |
| `_evaluate_legacy_heuristics` | `{"status", "advice"}` |
| `_evaluate_persona_inversion` | `{"status", "fluff_detected", "advice"}` |
| `_evaluate_cognitive_routing` | `{"status", "advice"}` |
| `_evaluate_sycophancy_rubrics` | `str` |
| `_evaluate_idpi_defenses` | `str` |

The report-building code then has to special-case the two string returns
versus the three dict returns. Normalize them all to a single dataclass
(e.g. `@dataclass class AuditResult: status: str; advice: str; details:
dict | None = None`).

### 2.12 🔵 Annotated return type of `_evaluate_cognitive_routing` is wrong

Signature declares `-> Dict[str, str]` but the function is consistent with
the `Dict[str, Any]` pattern used by its peers. Either tighten everyone to
`Dict[str, str]` or relax this one to `Dict[str, Any]`.

---

## 3. Style, typing, dead code

### 3.1 🔵 Unused imports

```2:3:README.md
import re
from typing import Dict, Any, List, Optional
```

`List` and `Optional` are never used. Drop them (or actually use them in
type annotations).

### 3.2 🔵 Hard-coded year "2026"

The docstrings advertise compliance with "2026 cognitive architectures" and
"the holistic 2026 prompt audit pipeline". This will age badly within
months. Drop the year or make it a constant.

### 3.3 🔵 Inconsistent quoting

The file mixes single and double quotes seemingly at random
(`'fluff_detected'` vs `"status"`). Adopt one (Black-style double quotes is
the de-facto Python standard) and run `black` / `ruff format` in CI.

### 3.4 🔵 Mixed use of `or` chains where `in {...}` would read better

```55:55:README.md
        if task_type == "math" or task_type == "finance":
```

```61:61:README.md
        elif task_type == "spatial" or task_type == "grid":
```

Use `if task_type in {"math", "finance"}:` etc.

### 3.5 🔵 Emoji in `print` output

The report begins with `## 🔬 Unified Context Engineering Engine: Master Audit`.
On Windows consoles using legacy code pages (cp1252) and on log pipelines
that do not declare UTF-8, this raises `UnicodeEncodeError`. If the emoji is
worth keeping, set `sys.stdout.reconfigure(encoding="utf-8")` in the demo
block or document the requirement.

### 3.6 🔵 Report formatting double-spaces

`run_master_audit` joins lines with `"\n"` while many appended strings
already end in `\n`, producing inconsistent blank-line spacing in the
output. Use a list of paragraphs joined with `"\n\n"`, or be explicit about
which lines carry their own trailing newline.

### 3.7 🔵 No module docstring, no `__all__`, no logging

For something that calls itself an "engine", the lack of a module
docstring, `__all__` export list, and any logging makes the file feel
ad-hoc. Even `logging.getLogger(__name__)` plus `logger.debug(...)` calls
in each evaluator would help users diagnose false positives.

---

## 4. Substantive / opinionated concerns

### 4.1 🟡 Pattern-matching as a proxy for prompt quality is fundamentally weak

Every check in this auditor is a single substring or one-line regex against
the literal text of the prompt. That means:

- Anyone aware of the auditor can defeat every check by adding the magic
  tokens (`<sandboxed_context>`, `1-5 scoring`, `Thought / Action /
  Observation`) without changing prompt behaviour at all.
- The auditor cannot distinguish a *real* ReAct schema from the literal
  sentence "Thought, action, and observation are important." That sentence
  passes `_evaluate_cognitive_routing` for agentic tasks.
- A well-engineered prompt that simply uses different vocabulary (e.g.
  "reasoning trace" instead of "thought") fails.

If the project is meant to be more than a demo, the checks should at least
work on tokenized structure (look for `Thought:`, `Action:`, `Observation:`
at line start), and ideally use a small LLM call to judge intent.

### 4.2 🟡 Some advice contradicts current best practice

> "Reasoning models already generate hidden internal thought traces.
> Forcing them to 'think step by step' is redundant, slows down response
> times, and interferes with native logic."

This is asserted with high confidence as a "Critical Warning", but the
empirical picture is more mixed: for non-reasoning models (the majority of
deployments) explicit CoT prompts still help, and for reasoning models the
penalty is small. Phrasing this as a hard error will produce noisy reports.
Soften to an informational note unless the auditor can detect the model
family it's targeting.

### 4.3 🟡 The persona advice is over-stated

> "Assigning overly complex personas limits the model, degrading factual
> accuracy and amplifying bias. Role prompting should solely be used to
> enforce tone and output formatting."

There is a real effect here but the phrasing "solely" overstates it. Many
production prompts ("You are a senior security engineer...") legitimately
benefit from role priming. The auditor should distinguish between
demographic fluff (the actual concern) and domain expertise framing (often
useful).

---

## 5. Suggested minimal patch (illustrative, not exhaustive)

```python
import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class TaskType(str, Enum):
    GENERAL = "general"
    MATH = "math"
    FINANCE = "finance"
    SPATIAL = "spatial"
    GRID = "grid"
    AGENTIC = "agentic"

@dataclass
class AuditResult:
    status: str
    advice: str
    details: dict | None = None

class ContextEngineeringAuditor:
    STEP_BY_STEP_RE = re.compile(r"step[\s-]+by[\s-]+step", re.IGNORECASE)
    RUBRIC_RE = re.compile(
        r"\b(\d+\s*[-–]\s*\d+\s*(scoring|scale|rating)|yes\s*/\s*no|true\s*/\s*false|likert)\b",
        re.IGNORECASE,
    )
    SPATIAL_RE = re.compile(r"\[x\]|[↑↓←→]")
    PERSONA_FLUFF = (
        "years old", "gender", "lives in", "married", "hobbies",
        "expert with", "years of experience",
    )

    def __init__(self) -> None:
        joined = "|".join(map(re.escape, self.PERSONA_FLUFF))
        self._fluff_re = re.compile(rf"\b({joined})\b", re.IGNORECASE)

    def run_master_audit(self, prompt: str, task_type: TaskType = TaskType.GENERAL) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        ...
```

The core point is: typed task types, compiled regexes, word boundaries,
explicit input validation, and a single result shape.

---

## 6. Quick triage summary

| # | Severity | Issue |
|---|----------|-------|
| 1.1 | 🟠 | Python code lives inside `README.md` |
| 1.2 | 🟡 | No tests, license, gitignore, lockfile, CI |
| 2.1 | 🔴 | `modality_order` regex precedence is wrong |
| 2.2 | 🟠 | `declarative_signature` and `modality_order` patterns are dead code |
| 2.3 | 🔴 | Spatial regex matches the letter `x`, false-passing most prompts |
| 2.4 | 🟠 | `step-by-step` substring check misses common variants |
| 2.5 | 🟠 | Persona fluff list matched with raw `in` causes false positives |
| 2.6 | 🟡 | Rubric regex too narrow (only `1-5 scoring`, `Yes/No`, `strict criteria`) |
| 2.7 | 🟠 | IDPI check is tag-presence theater, advice oversells "sandboxing" |
| 2.8 | 🟡 | Unknown `task_type` silently returns "Optimal" with a false message |
| 2.9 | 🟡 | `task_type` should be `Enum` / `Literal` |
| 2.10 | 🟡 | No input validation; empty prompt audits as all-Optimal |
| 2.11 | 🔵 | Inconsistent return shapes between evaluators |
| 2.12 | 🔵 | Wrong return-type annotation on `_evaluate_cognitive_routing` |
| 3.1 | 🔵 | Unused imports (`List`, `Optional`) |
| 3.2 | 🔵 | Hard-coded "2026" in docstrings |
| 3.3 | 🔵 | Inconsistent quoting style |
| 3.4 | 🔵 | `or` chains where `in {...}` reads better |
| 3.5 | 🔵 | Emoji in `print` breaks non-UTF-8 stdout |
| 3.6 | 🔵 | Output joining produces inconsistent blank lines |
| 3.7 | 🔵 | No module docstring, `__all__`, or logging |
| 4.1 | 🟡 | Substring/regex checks are easy to fool and miss paraphrases |
| 4.2 | 🟡 | "Step-by-step is harmful" stated too absolutely |
| 4.3 | 🟡 | Persona advice ("solely … tone and formatting") is over-stated |

The two issues I would fix first are **2.3** (the spatial regex bug, which
makes the corresponding audit silently useless) and **1.1** (move the code
out of `README.md` so it can actually be run and tested). Everything else
becomes much easier to address once a real Python module and a test file
exist.
