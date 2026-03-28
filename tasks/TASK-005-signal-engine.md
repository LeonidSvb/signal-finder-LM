---
description: Signal engine — parallel LLM calls per ICP, selects signals from library
globs: core/signal_engine.py, core/prompts/signal_prompt.txt
alwaysApply: false
---

id: "TASK-005"
title: "Signal engine — generate signals per ICP (parallel LLM calls)"
status: "done"
priority: "P0"
labels: ["llm", "core", "signals", "parallel"]
dependencies: ["tasks/TASK-003-icp-engine.md", "tasks/TASK-004-signals-library.md"]
created: "2026-03-28"

# 1) High-Level Objective

For each selected ICP, make a separate LLM call that selects and adapts 5–8 signals from the signals library. Calls run in parallel. Output is a dict mapping each ICP to its signals list.

# 2) Background / Context

Parallel calls per ICP improve output quality — each call has focused context for one specific ICP. LLM must select from SIGNALS_LIBRARY only (injected as context). No invented signals allowed. The result drives both the UI display and Exa filtering.

# 3) Assumptions & Constraints

- ASSUMPTION: User selects 2–3 ICPs, so 2–3 parallel LLM calls
- Constraint: Prompt lives in `core/prompts/signal_prompt.txt` — signals library injected at runtime
- Constraint: LLM must return signal names that exactly match names in SIGNALS_LIBRARY
- Constraint: Use concurrent.futures.ThreadPoolExecutor for parallel calls

# 4) Dependencies

- TASK-003 (ICP model, llm_client.py)
- TASK-004 (SIGNALS_LIBRARY, Signal model)

# 5) Context Plan

**Beginning:**
- core/models.py _(read-only)_
- core/signals_library.py _(read-only)_
- services/llm_client.py _(read-only)_
- config/settings.py _(read-only)_

**End state:**
- core/prompts/signal_prompt.txt
- core/signal_engine.py
- core/models.py (ICPSignals dataclass added)

# 6) Low-Level Steps

1. **Add ICPSignals dataclass to core/models.py**

   - File: `core/models.py`
   - Add:
     ```python
     @dataclass
     class ICPSignals:
         icp: ICP
         signals: list[Signal]         # top 5 shown by default
         hidden_signals: list[Signal]  # additional, shown on expand
     ```

2. **Write signal_prompt.txt**

   - File: `core/prompts/signal_prompt.txt`
   - System prompt that:
     - Receives: ICP description + full signals library as text
     - Returns: JSON list of signal names from the library relevant to this ICP
     - Sorted: most relevant first
     - Format: `["Signal Name 1", "Signal Name 2", ...]` — exact names only
     - Count: 5–8 signals per ICP
     - Rule: only names that exist in the provided library

3. **Implement generate_signals_for_icp(icp: ICP) -> ICPSignals**

   - File: `core/signal_engine.py`
   - Function:
     ```python
     def generate_signals_for_icp(icp: ICP) -> ICPSignals:
         """
         Single LLM call for one ICP.
         Returns ICPSignals with signals split: first 5 visible, rest hidden.
         """
     ```
   - Details:
     - Load `core/prompts/signal_prompt.txt`
     - Inject `signals_as_context_string()` into prompt
     - User message: formatted ICP description
     - Parse JSON response → list of signal name strings
     - Resolve each name via `get_signal_by_name(name)` — skip unresolvable names
     - Split: signals[:5] → visible, signals[5:] → hidden

4. **Implement generate_signals_parallel(icps: list[ICP]) -> list[ICPSignals]**

   - File: `core/signal_engine.py`
   - Function:
     ```python
     def generate_signals_parallel(icps: list[ICP]) -> list[ICPSignals]:
         """
         Runs generate_signals_for_icp for each ICP in parallel.
         Returns list preserving input order.
         """
     ```
   - Details:
     - Use `concurrent.futures.ThreadPoolExecutor(max_workers=3)`
     - Preserve order of input icps in output

# 7) Types & Interfaces

```python
# core/models.py
@dataclass
class ICPSignals:
    icp: ICP
    signals: list[Signal]
    hidden_signals: list[Signal]
```

# 8) Acceptance Criteria

- `generate_signals_parallel([icp1, icp2])` returns 2 ICPSignals objects
- Each ICPSignals has 5 visible signals and 0–3 hidden signals
- All signal names resolve to objects from SIGNALS_LIBRARY (no hallucinated signals in output)
- Both calls complete in roughly the same time (parallel, not sequential)

# 9) Testing Strategy

- Manual: create 2 test ICP objects → call generate_signals_parallel → inspect signal names match library
- Manual: time the call — parallel 2-ICP run should be ~same duration as single call

# 10) Notes

- ThreadPoolExecutor is sufficient — Groq is fast enough, no need for async
- If LLM returns a signal name not in library, silently skip it (don't crash)
