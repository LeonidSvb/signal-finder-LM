---
description: Exa engine — find real companies using searchable signals per ICP
globs: core/exa_engine.py, services/exa_client.py, core/prompts/exa_processing_prompt.txt, core/models.py
alwaysApply: false
---

id: "TASK-006"
title: "Exa engine — discover real companies via searchable signals"
status: "done"
priority: "P0"
labels: ["exa", "core", "companies"]
dependencies: ["tasks/TASK-005-signal-engine.md"]
created: "2026-03-28"

# 1) High-Level Objective

For each ICP + its signals, construct Exa queries using only `searchable: True` signals. Return 2–3 real companies per ICP (3–6 total). Each company includes: name, signal detected, explanation, source URL.

# 2) Background / Context

This is the most important block in the report — real companies showing real signals. Exa searches the open web for recent events (funding, M&A, leadership changes, etc.). LLM then extracts structured company data from Exa raw results. No fake companies allowed — if Exa returns nothing, show nothing.

# 3) Assumptions & Constraints

- ASSUMPTION: Exa neural search handles open-ended queries well for news/funding events
- Constraint: Only `searchable: True` signals passed to Exa
- Constraint: 2–3 companies per ICP max, 3–6 total
- Constraint: If Exa returns empty results for a signal — skip, try next signal
- Constraint: exa_processing_prompt.txt extracts structured data from raw Exa results

# 4) Dependencies

- TASK-005 (ICPSignals with searchable signals)

# 5) Context Plan

**Beginning:**
- core/models.py _(read-only)_
- core/signals_library.py _(read-only)_
- config/settings.py _(read-only)_

**End state:**
- services/exa_client.py
- core/prompts/exa_processing_prompt.txt
- core/models.py (Company dataclass added)
- core/exa_engine.py

# 6) Low-Level Steps

1. **Add Company dataclass to core/models.py**

   - File: `core/models.py`
   - Add:
     ```python
     @dataclass
     class Company:
         name: str
         signal: str          # signal name that triggered discovery
         explanation: str     # why this matters for the recruiter
         source_url: str = "" # optional — Exa result URL
         icp_ref: str = ""    # which ICP this company belongs to
     ```

2. **Create services/exa_client.py**

   - File: `services/exa_client.py`
   - Contents:
     ```python
     from exa_py import Exa
     from config.settings import EXA_API_KEY

     _client = Exa(api_key=EXA_API_KEY)

     def search(query: str, num_results: int = 5) -> list[dict]:
         """
         Runs neural search. Returns list of dicts with keys: title, url, text.
         Returns empty list on error.
         """
         try:
             results = _client.search_and_contents(
                 query,
                 num_results=num_results,
                 text=True,
             )
             return [
                 {"title": r.title, "url": r.url, "text": r.text or ""}
                 for r in results.results
             ]
         except Exception:
             return []
     ```

3. **Write exa_processing_prompt.txt**

   - File: `core/prompts/exa_processing_prompt.txt`
   - System prompt that:
     - Receives: ICP description + signal name + raw Exa search results (title + snippet)
     - Returns: JSON list of companies, format:
       ```json
       [{"name": "...", "signal": "...", "explanation": "...", "source_url": "..."}]
       ```
     - Max 3 items
     - Rule: only include companies where signal is clearly present in the source
     - Rule: explanation must be 1 sentence, specific to why recruiter should care
     - Rule: if no clear match found, return empty list `[]`

4. **Implement find_companies_for_icp(icp_signals: ICPSignals) -> list[Company]**

   - File: `core/exa_engine.py`
   - Function:
     ```python
     def find_companies_for_icp(icp_signals: ICPSignals) -> list[Company]:
         """
         Runs Exa queries for searchable signals of one ICP.
         Returns up to MAX_COMPANIES_PER_ICP companies.
         """
     ```
   - Details:
     - Filter signals: only `signal.searchable == True`
     - For each searchable signal, build query: `"{signal.name} {icp.industry} {icp.geography or 'USA'} last 30 days"`
     - Call `exa_client.search(query, num_results=5)`
     - Pass results to LLM via exa_processing_prompt.txt
     - Parse JSON → list of Company objects
     - Stop when MAX_COMPANIES_PER_ICP (3) reached
     - Set `company.icp_ref` to icp role

5. **Implement find_all_opportunities(icp_signals_list: list[ICPSignals]) -> list[Company]**

   - File: `core/exa_engine.py`
   - Function:
     ```python
     def find_all_opportunities(icp_signals_list: list[ICPSignals]) -> list[Company]:
         """
         Runs find_companies_for_icp for each ICP sequentially.
         Returns deduplicated list capped at MAX_COMPANIES_TOTAL (6).
         """
     ```
   - Details:
     - Deduplicate by company name (case-insensitive)
     - Cap total at MAX_COMPANIES_TOTAL

# 7) Types & Interfaces

```python
# core/models.py
@dataclass
class Company:
    name: str
    signal: str
    explanation: str
    source_url: str = ""
    icp_ref: str = ""
```

# 8) Acceptance Criteria

- `find_all_opportunities(icp_signals_list)` returns 1–6 Company objects with real names
- No duplicate companies in output
- Each Company has name, signal, explanation populated
- If all Exa queries return empty — function returns empty list (no crash)

# 9) Testing Strategy

- Manual: create ICPSignals with 2 ICPs (e.g., healthcare staffing + tech recruiting) → call find_all_opportunities → inspect company names are real
- Manual: verify source_url values are valid URLs

# 10) Notes

- Exa neural search works best with natural language queries — keep query format: `[signal] [industry] [region] last 30 days`
- LLM processing step ensures we extract clean structured data from Exa's raw text snippets
