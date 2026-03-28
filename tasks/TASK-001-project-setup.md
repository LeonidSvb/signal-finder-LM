---
description: Project scaffolding — folder structure, config, API keys, settings
globs: config/**, main.py, requirements.txt
alwaysApply: false
---

id: "TASK-001"
title: "Project scaffolding — structure, config, secrets"
status: "done"
priority: "P0"
labels: ["setup", "config"]
dependencies: []
created: "2026-03-28"

# 1) High-Level Objective

Create the full project folder structure, requirements.txt, and config/settings.py with all hardcoded API keys and constants. No logic — only skeleton and config.

# 2) Background / Context

This is a stateless mini-SaaS lead magnet. No database, no auth. All secrets are hardcoded in config (tool is for internal biz dev use only — not exposed to end users to configure).

# 3) Assumptions & Constraints

- ASSUMPTION: Python 3.11+
- Constraint: No .env file loading — values hardcoded directly in config/settings.py
- Constraint: No database, no auth layer

# 4) Dependencies

- None

# 5) Context Plan

**Beginning:**
- PRD-signal-finder.md _(read-only)_

**End state (must exist after completion):**
- requirements.txt
- config/settings.py
- core/__init__.py
- core/prompts/ (empty folder with .gitkeep)
- services/__init__.py
- utils/__init__.py
- ui/__init__.py
- analytics/__init__.py
- main.py (stub only — `pass`)

# 6) Low-Level Steps

1. **Create requirements.txt**

   - File: `requirements.txt`
   - Contents:
     ```
     streamlit
     requests
     beautifulsoup4
     groq
     exa-py
     posthog
     ```

2. **Create config/settings.py**

   - File: `config/settings.py`
   - Contents:
     ```python
     EXA_API_KEY = os.getenv("EXA_API_KEY", "")
     GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
     GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

     BOOKING_URL = "https://cal.com/leonidshvorob/fit-check-call"
     CONTACT_EMAIL = "leo@systemhustle.com"
     WEBSITE_URL = "https://systemhustle.com"
     WHATSAPP = "+628175755953"

     MAX_ICPS_SELECTABLE = 3
     MIN_ICPS_SELECTABLE = 2
     MAX_COMPANIES_TOTAL = 6
     MAX_COMPANIES_PER_ICP = 3
     MAX_SIGNALS_VISIBLE = 5
     MAX_RESPONSE_TIME_SECONDS = 20

     POSTHOG_API_KEY = ""  # fill when ready
     POSTHOG_HOST = "https://app.posthog.com"
     ```

3. **Create all __init__.py files and folder stubs**

   - `core/__init__.py` — empty
   - `core/prompts/.gitkeep` — empty
   - `services/__init__.py` — empty
   - `utils/__init__.py` — empty
   - `ui/__init__.py` — empty
   - `analytics/__init__.py` — empty

4. **Create main.py stub**

   - File: `main.py`
   - Contents:
     ```python
     import argparse

     def main():
         parser = argparse.ArgumentParser(description="Signal Finder — CLI mode")
         parser.add_argument("--url", required=True, help="Company website URL")
         args = parser.parse_args()
         # orchestrator call will go here in TASK-007
         print(f"URL received: {args.url}")

     if __name__ == "__main__":
         main()
     ```

# 7) Types & Interfaces

N/A — pure config, no data models yet.

# 8) Acceptance Criteria

- `python main.py --url="https://example.com"` runs without error and prints the URL
- `config/settings.py` importable: `from config.settings import EXA_API_KEY` works
- All folders exist with `__init__.py`

# 9) Testing Strategy

- Manual: `python main.py --url="https://example.com"` and verify output
- Manual: `python -c "from config.settings import EXA_API_KEY; print(EXA_API_KEY)"` returns the key

# 10) Notes

- Groq model: llama-3.3-70b-versatile (fast, cheap, strong enough for ICP/signal generation)
- Exa key from memory, Groq key provided by user
