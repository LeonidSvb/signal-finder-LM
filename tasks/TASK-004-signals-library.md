---
description: Signals library — structured catalog of 15 hiring signals with searchability flag
globs: core/signals_library.py, core/models.py
alwaysApply: false
---

id: "TASK-004"
title: "Signals library — catalog of 15 hiring signals"
status: "done"
priority: "P0"
labels: ["core", "signals", "data"]
dependencies: ["tasks/TASK-001-project-setup.md"]
created: "2026-03-28"

# 1) High-Level Objective

Build a structured, hardcoded signals catalog in Python. This is the ground truth for all signal generation. LLM selects from this library — never invents new signals.

# 2) Background / Context

Two types of signals exist:
- `searchable: True` — Exa AI can find real companies matching these (funding, M&A, leadership change, etc.)
- `searchable: False` — user must find manually (job board postings, career page changes, hiring spikes)

Both types are shown in the report. Only `searchable: True` signals are passed to Exa.

# 3) Assumptions & Constraints

- Constraint: Catalog is hardcoded — not loaded from file or DB
- Constraint: Signal names must be stable strings (used as keys in downstream logic)
- Constraint: All 15 signals from PRD must be present

# 4) Dependencies

- TASK-001 (core/models.py exists)

# 5) Context Plan

**Beginning:**
- PRD-signal-finder.md _(read-only)_
- core/models.py _(read-only)_

**End state:**
- core/models.py (Signal dataclass added)
- core/signals_library.py

# 6) Low-Level Steps

1. **Add Signal dataclass to core/models.py**

   - File: `core/models.py`
   - Add:
     ```python
     from dataclasses import dataclass, field

     @dataclass
     class Signal:
         name: str
         description: str
         category: str        # "early" | "late" | "structural"
         searchable: bool
         sources: list[str]
     ```

2. **Build SIGNALS_LIBRARY in core/signals_library.py**

   - File: `core/signals_library.py`
   - Define `SIGNALS_LIBRARY: list[Signal]` with all 15 signals:
     1. Hiring Spike — late, searchable=False, sources=[LinkedIn Jobs, Indeed]
     2. Long-Open Roles (30+ days) — late, searchable=False, sources=[LinkedIn Jobs, Indeed]
     3. Leadership Change (Head of Talent / VP Eng / Head of Sales) — structural, searchable=True, sources=[LinkedIn, news]
     4. Funding Event (Seed / Series A–C) — early, searchable=True, sources=[Crunchbase, news]
     5. Geographic / Operational Expansion — early, searchable=True, sources=[news, press releases]
     6. M&A (merger or acquisition) — structural, searchable=True, sources=[news]
     7. New Product / Business Unit Launch — early, searchable=True, sources=[company blog, news]
     8. Role-Specific Hiring Surge (10+ same function) — late, searchable=False, sources=[job boards]
     9. Career Page Expansion — late, searchable=False, sources=[company website]
     10. Public Hiring Announcements (CEO/HR posts) — late, searchable=True, sources=[LinkedIn]
     11. High Turnover Signals — structural, searchable=False, sources=[LinkedIn]
     12. Compliance / Regulatory Pressure — structural, searchable=True, sources=[regulatory news]
     13. New Large Contract Signed — early, searchable=True, sources=[news]
     14. Tech Stack Change / Transformation — structural, searchable=True, sources=[engineering blogs, news]
     15. Layoffs → Rebuild Phase — structural, searchable=True, sources=[news]

3. **Add helper functions**

   - File: `core/signals_library.py`
   - Add:
     ```python
     def get_all_signals() -> list[Signal]: ...
     def get_searchable_signals() -> list[Signal]: ...
     def get_signal_by_name(name: str) -> Signal | None: ...
     def signals_as_context_string() -> str:
         """Returns signals formatted as text for LLM context injection."""
     ```

# 7) Types & Interfaces

```python
# core/models.py
@dataclass
class Signal:
    name: str
    description: str
    category: str
    searchable: bool
    sources: list[str]
```

# 8) Acceptance Criteria

- `get_all_signals()` returns exactly 15 Signal objects
- `get_searchable_signals()` returns only signals where searchable=True (expected: 10)
- `signals_as_context_string()` returns a readable string suitable for LLM prompt injection
- `get_signal_by_name("Funding Event")` returns the correct Signal object

# 9) Testing Strategy

- Manual: `from core.signals_library import get_all_signals; print(len(get_all_signals()))` → 15
- Manual: `from core.signals_library import get_searchable_signals; print(len(get_searchable_signals()))` → 10

# 10) Notes

- signals_as_context_string() is injected into signal_prompt.txt at runtime so LLM knows the exact catalog
