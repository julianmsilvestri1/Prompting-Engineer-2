# AGENTS.md

## Cursor Cloud specific instructions

### Overview

This repository contains a single Python class (`ContextEngineeringAuditor`) that audits LLM prompts against various quality and security heuristics. The Python source code is embedded inside `README.md` (not in a separate `.py` file). `CODE_REVIEW.md` contains a detailed code review.

### Running the code

The Python code lives in `README.md` with a markdown header (`# Prompting-Engineer-2`) on line 1. To execute it, skip the first line:

```bash
tail -n +2 README.md | python3 -
```

This runs the built-in demo which audits a sample "flawed prompt" and prints an audit report.

### Dependencies

- **Python 3.x** (only standard library modules `re` and `typing` are used — no external packages required)
- No `requirements.txt`, `pyproject.toml`, or package manager configuration exists

### Linting / Testing

- There are no automated tests or test framework configured in this repository.
- There is no linter or formatter configuration. You can lint with `python3 -m py_compile` by extracting the code first, or run `tail -n +2 README.md | python3 -m py_compile -` (note: `py_compile` doesn't accept stdin — use the syntax check approach below instead).
- To syntax-check: `python3 -c "$(tail -n +2 README.md)"` — this compiles and executes the code, verifying both syntax and runtime correctness.

### Key gotchas

- Do **not** run `python3 README.md` directly — it fails because line 1 is a markdown header, not valid Python.
- The code has zero external dependencies, so there is nothing to install.
