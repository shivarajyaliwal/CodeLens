# Interactive Code Explanation Bot

A lightweight AST-driven web app for explaining Python code step-by-step.

## Features

- Parse Python source into an AST and walk each construct.
- Generate line-by-line explanation bullets.
- Estimate time-complexity from loop depth and recursion patterns.
- Suggest alternative implementation/optimization ideas.
- Provide a simple interactive UI for pasting code and getting explanations.

## Run locally

```bash
python app.py
```

Open http://localhost:8000.

## Test

```bash
pytest
```
