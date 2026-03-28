---
description: Orchestrator — full pipeline coordination + action/insight generation
globs: core/orchestrator.py, core/prompts/action_prompt.txt, core/prompts/system_context.txt, utils/formatter.py
alwaysApply: false
---

id: "TASK-007"
title: "Orchestrator — pipeline coordination, action block, insight block, final JSON"
status: "done"
priority: "P0"
labels: ["core", "orchestrator", "pipeline"]
dependencies: ["tasks/TASK-006-exa-engine.md"]
created: "2026-03-28"

# 1) High-Level Objective

Wire all engines into a single pipeline function `run_full_analysis(url, selected_icp_indices)`. Also generate the action block and insight block via LLM. Return strict JSON report.

# 2) Background / Context

The orchestrator is the only entry point for both CLI and UI. It coordinates: scrape → ICP generation → signal generation (parallel) → Exa discovery → action/insight generation → final report assembly.

# 3) Assumptions & Constraints

- ASSUMPTION: selected_icp_indices passed from UI after user selects ICPs
- Constraint: run_full_analysis must complete in ~20 seconds total
- Constraint: Returns strict JSON — UI and CLI both consume the same output
- Constraint: Prompts for action and insight in `core/prompts/` files

# 4) Dependencies

- TASK-002 (scraper)
- TASK-003 (icp_engine)
- TASK-005 (signal_engine)
- TASK-006 (exa_engine)

# 5) Context Plan

**Beginning:**
- core/models.py _(read-only)_
- core/icp_engine.py _(read-only)_
- core/signal_engine.py _(read-only)_
- core/exa_engine.py _(read-only)_
- utils/scraper.py _(read-only)_
- config/settings.py _(read-only)_

**End state:**
- core/prompts/action_prompt.txt
- core/prompts/system_context.txt
- core/orchestrator.py
- utils/formatter.py

# 6) Low-Level Steps

1. **Add Report dataclass to core/models.py**

   - File: `core/models.py`
   - Add:
     ```python
     @dataclass
     class ActionPlan:
         who_to_target: list[str]   # specific roles
         where_to_find: list[str]   # LinkedIn patterns, job boards
         outreach_angles: list[str] # 1-2 example angles

     @dataclass
     class Report:
         icp_list: list[ICP]
         icp_signals: list[ICPSignals]
         companies: list[Company]
         insight: str
         action_plan: ActionPlan
         cta_url: str
     ```

2. **Write action_prompt.txt**

   - File: `core/prompts/action_prompt.txt`
   - System prompt that receives: selected ICPs + detected signals + found companies
   - Returns JSON:
     ```json
     {
       "who_to_target": ["..."],
       "where_to_find": ["..."],
       "outreach_angles": ["..."],
       "insight": "..."
     }
     ```
   - who_to_target: 3–5 specific role titles to reach out to
   - where_to_find: 2–3 specific sources/search patterns
   - outreach_angles: 1–2 signal-based opening lines
   - insight: "You're missing this" — 2 sentences comparing current approach vs signal-based approach

3. **Write system_context.txt**

   - File: `core/prompts/system_context.txt`
   - Global system context injected into all LLM calls:
     - Role: signal intelligence system for recruiting/staffing BD
     - Operator: System Hustle (systemhustle.com)
     - Output format: always structured JSON unless told otherwise
     - Tone: professional, direct, specific

4. **Implement run_full_analysis(url: str, selected_indices: list[int]) -> Report**

   - File: `core/orchestrator.py`
   - Function:
     ```python
     def run_full_analysis(url: str, selected_indices: list[int]) -> Report:
         """
         Full pipeline. selected_indices are indices into icp_list from generate_icp().
         Returns Report dataclass.
         """
     ```
   - Steps in order:
     1. `website_text = scrape_website(url)`
     2. `all_icps = generate_icp(website_text)` → returns 8–10 ICPs
     3. `selected_icps = [all_icps[i] for i in selected_indices]`
     4. `icp_signals = generate_signals_parallel(selected_icps)`
     5. `companies = find_all_opportunities(icp_signals)`
     6. Call LLM with action_prompt.txt → parse ActionPlan + insight
     7. Return `Report(icp_list=all_icps, icp_signals=icp_signals, companies=companies, insight=..., action_plan=..., cta_url=BOOKING_URL)`

5. **Add generate_icp_only(url: str) -> list[ICP] to orchestrator**

   - File: `core/orchestrator.py`
   - Needed by UI for Step 2 (show ICPs before user selects)
   - Function:
     ```python
     def generate_icp_only(url: str) -> list[ICP]:
         website_text = scrape_website(url)
         return generate_icp(website_text)
     ```

6. **Implement report_to_dict(report: Report) -> dict in utils/formatter.py**

   - File: `utils/formatter.py`
   - Converts Report dataclass to JSON-serializable dict for CLI output

# 7) Types & Interfaces

```python
# core/models.py
@dataclass
class ActionPlan:
    who_to_target: list[str]
    where_to_find: list[str]
    outreach_angles: list[str]

@dataclass
class Report:
    icp_list: list[ICP]
    icp_signals: list[ICPSignals]
    companies: list[Company]
    insight: str
    action_plan: ActionPlan
    cta_url: str
```

# 8) Acceptance Criteria

- `run_full_analysis("https://systemhustle.com", [0, 1])` returns a Report with all fields populated
- `generate_icp_only("https://systemhustle.com")` returns 8–10 ICP objects
- `report_to_dict(report)` returns valid JSON-serializable dict

# 9) Testing Strategy

- Manual end-to-end: `python main.py --url="https://systemhustle.com"` → full pipeline runs, JSON printed to stdout
- Manual: verify companies in output are real (names are actual companies)
- Manual: verify action plan has specific, non-generic content

# 10) Notes

- action_prompt.txt should receive a summary of all ICPs + signals + companies as context — keep it under 3000 tokens
- system_context.txt is prepended to all LLM calls as additional context
