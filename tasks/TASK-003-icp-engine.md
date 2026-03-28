---
description: ICP engine — LLM generates 8-10 ideal client profiles from scraped website text
globs: core/icp_engine.py, core/prompts/icp_prompt.txt, core/models.py
alwaysApply: false
---

id: "TASK-003"
title: "ICP engine — generate ideal client profiles from website context"
status: "done"
priority: "P0"
labels: ["llm", "core", "icp"]
dependencies: ["tasks/TASK-001-project-setup.md", "tasks/TASK-002-scraper.md"]
created: "2026-03-28"

# 1) High-Level Objective

Given scraped website text, call Groq LLM and return 8–10 ICPs sorted by relevance. Each ICP describes the type of company the recruiter/agency should target as a client.

# 2) Background / Context

The recruiter inputs their own site. The system infers what kinds of companies they best serve (their ICPs). These ICPs drive everything downstream: signal generation and Exa search. LLM must select from structured output only — no free-form descriptions.

# 3) Assumptions & Constraints

- ASSUMPTION: Website text is sufficient to infer niche (healthcare staffing vs tech recruiting vs general)
- Constraint: Output must be strict JSON list — no markdown, no explanation text
- Constraint: Prompt lives in `core/prompts/icp_prompt.txt` — not inline in code
- Constraint: No numeric relevance score in output (sorted by position only)

# 4) Dependencies

- TASK-001 (config/settings.py, services/llm_client.py skeleton)
- TASK-002 (scrape_website returns text)

# 5) Context Plan

**Beginning:**
- config/settings.py _(read-only)_
- PRD-signal-finder.md _(read-only)_

**End state:**
- core/models.py (ICP dataclass)
- core/prompts/icp_prompt.txt
- core/icp_engine.py
- services/llm_client.py

# 6) Low-Level Steps

1. **Define ICP dataclass in core/models.py**

   - File: `core/models.py`
   - Contents:
     ```python
     from dataclasses import dataclass
     from typing import Optional

     @dataclass
     class ICP:
         role: str            # e.g. "Head of Talent"
         company_type: str    # e.g. "Series A SaaS startup"
         industry: str        # e.g. "Technology"
         geography: Optional[str] = None  # only if confident
     ```

2. **Create services/llm_client.py**

   - File: `services/llm_client.py`
   - Contents:
     ```python
     from groq import Groq
     from config.settings import GROQ_API_KEY, GROQ_MODEL

     _client = Groq(api_key=GROQ_API_KEY)

     def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
         response = _client.chat.completions.create(
             model=GROQ_MODEL,
             messages=[
                 {"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_prompt}
             ],
             temperature=temperature,
         )
         return response.choices[0].message.content
     ```

3. **Write icp_prompt.txt**

   - File: `core/prompts/icp_prompt.txt`
   - Contents: system prompt instructing LLM to analyze agency positioning and return JSON list of ICPs
   - Must include:
     - Role in this system (analyzing a recruiting/staffing agency website)
     - Strict JSON output format: `[{"role": "...", "company_type": "...", "industry": "...", "geography": "..."}]`
     - Instruction: geography only if clearly implied, else omit
     - Instruction: sort by most likely to convert, most relevant first
     - Instruction: return exactly 8–10 items, no more, no less
     - Instruction: no markdown, no explanation, JSON only

4. **Implement generate_icp(website_text: str) -> list[ICP]**

   - File: `core/icp_engine.py`
   - Exported API:
     ```python
     def generate_icp(website_text: str) -> list[ICP]:
         """
         Calls LLM with icp_prompt.txt + website_text.
         Parses JSON response into list of ICP dataclasses.
         Raises ValueError if JSON parse fails.
         """
     ```
   - Details:
     - Load prompt from `core/prompts/icp_prompt.txt`
     - Call `call_llm(system_prompt, website_text)`
     - Strip markdown fences if present (```json ... ```)
     - Parse JSON → list of ICP objects
     - Validate: must be 6–10 items (allow slight variance), each must have role + company_type + industry

# 7) Types & Interfaces

```python
# core/models.py
@dataclass
class ICP:
    role: str
    company_type: str
    industry: str
    geography: Optional[str] = None
```

# 8) Acceptance Criteria

- `generate_icp(text)` returns list of 8–10 ICP objects
- Each ICP has role, company_type, industry populated
- Calling with systemhustle.com scraped text returns recruiting-relevant ICPs
- No raw JSON strings in return value — only ICP dataclasses

# 9) Testing Strategy

- Manual: scrape systemhustle.com → pass to generate_icp → inspect output relevance
- Manual: pass garbage text → confirm it still returns structured output (not crash)

# 10) Notes

- Temperature 0.3 keeps output consistent across runs
- If LLM wraps in markdown fences — strip before json.loads()
