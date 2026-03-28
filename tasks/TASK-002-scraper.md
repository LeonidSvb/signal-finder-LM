---
description: Website scraper — extract clean positioning text via Exa get_contents with summary
globs: utils/scraper.py
alwaysApply: false
---

id: "TASK-002"
title: "Website scraper — Exa get_contents primary, BS4 fallback"
status: "done"
priority: "P0"
labels: ["scraping", "utils", "exa"]
dependencies: ["tasks/TASK-001-project-setup.md"]
created: "2026-03-28"

# 1) High-Level Objective

Fetch company website content via Exa `get_contents()` with built-in LLM summary. Returns clean, positioning-focused text ready for ICP generation. BS4 fallback only if Exa fails.

# 2) Background / Context

Exa `get_contents()` accepts a URL directly (no search needed), returns LLM-generated summary scoped to a custom query. At $1/1000 requests it's cheap enough to use as primary. Handles JS-heavy sites, redirects, and paywalls better than raw HTML parsing. The summary query is scoped to recruiting agency positioning so the ICP engine receives only relevant context.

# 3) Assumptions & Constraints

- ASSUMPTION: Exa handles all common site types (static HTML, React SPA, Webflow, Squarespace)
- Constraint: Use `summary` feature with a targeted positioning query — not raw text dump
- Constraint: Also fetch subpages (about, services) via `subpages=2`
- Constraint: Output must be plain text under 4000 tokens (~16K chars)
- Constraint: BS4 fallback only triggered if Exa returns empty or throws

# 4) Dependencies

- TASK-001 (config/settings.py with EXA_API_KEY, services/exa_client.py skeleton)

# 5) Context Plan

**Beginning:**
- config/settings.py _(read-only)_

**End state:**
- utils/scraper.py

# 6) Low-Level Steps

1. **Implement scrape_website(url: str) -> str**

   - File: `utils/scraper.py`
   - Exported API:
     ```python
     def scrape_website(url: str) -> str:
         """
         Primary: Exa get_contents with LLM summary.
         Fallback: requests + BeautifulSoup if Exa returns empty or throws.
         Returns clean plain text focused on positioning/services/clients.
         Raises ValueError if both methods fail.
         """
     ```

2. **Primary path: _scrape_with_exa(url: str) -> str**

   - File: `utils/scraper.py` (private)
   - Implementation:
     ```python
     from exa_py import Exa
     from config.settings import EXA_API_KEY

     _exa = Exa(api_key=EXA_API_KEY)

     SUMMARY_QUERY = (
         "What does this company do, who are their target clients, "
         "what industries do they serve, what is their value proposition, "
         "what services or products do they offer"
     )

     def _scrape_with_exa(url: str) -> str:
         results = _exa.get_contents(
             urls=[url],
             summary={"query": SUMMARY_QUERY},
             subpages=2,
             subpage_target=["about", "services"],
         )
         parts = []
         for item in results.results:
             if item.summary:
                 parts.append(item.summary)
         return "\n\n".join(parts).strip()
     ```
   - Returns empty string (not raises) on Exa error — fallback handles it

3. **Fallback path: _scrape_with_bs4(url: str) -> str**

   - File: `utils/scraper.py` (private)
   - Same logic as original BS4 implementation:
     - Normalize URL, set User-Agent header, timeout 10s
     - Extract: `<title>`, `<meta name="description">`, `<h1>`, `<h2>`, `<h3>`, `<p>`, `<li>`
     - Remove: `<nav>`, `<footer>`, `<header>`, `<script>`, `<style>`, `<form>`
     - Try `{base_url}/about` and `{base_url}/services` — skip silently on 404
     - Join, strip whitespace, truncate to 16000 chars
     - Returns empty string on any exception

4. **Main function logic**

   ```python
   def scrape_website(url: str) -> str:
       if not url.startswith("http"):
           url = "https://" + url

       text = _scrape_with_exa(url)

       if len(text) < 200:
           text = _scrape_with_bs4(url)

       if len(text) < 100:
           raise ValueError(f"Could not extract content from: {url}")

       return text[:16000]
   ```

# 7) Types & Interfaces

```python
# utils/scraper.py
def scrape_website(url: str) -> str: ...
def _scrape_with_exa(url: str) -> str: ...
def _scrape_with_bs4(url: str) -> str: ...
```

# 8) Acceptance Criteria

- `scrape_website("https://systemhustle.com")` returns text clearly describing recruiting/BD positioning
- `scrape_website("https://nonexistent-xyz-site.com")` raises `ValueError`
- Output is focused on positioning/clients/services — not nav links or footer garbage
- Output is under 16000 chars

# 9) Testing Strategy

- Manual: `scrape_website("https://systemhustle.com")` — inspect that output describes System Hustle's services
- Manual: test a React SPA site — verify Exa handles it where BS4 would return near-empty
- Manual: test with bad URL — confirm ValueError raised

# 10) Notes

- `subpages=2` + `subpage_target=["about", "services"]` tells Exa to also pull those subpages and include in summary
- SUMMARY_QUERY is the key lever — scoped to positioning context so LLM summary skips irrelevant content
- BS4 kept as fallback: free, zero API calls, handles edge cases where Exa is rate-limited
